"""Service layer for Analytics operations."""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import case, extract, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.analytics import Birth, MassAttendance, PopulationSnapshot
from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.mass_times import MassTime
from app.models.person import Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.schemas.analytics import (
    AttendanceTrend,
    AttendanceTrendExtended,
    BirthCreate,
    BirthStatistics,
    BirthUpdate,
    MassAttendanceCreate,
    MassAttendanceUpdate,
    MassTimeBreakdown,
    PopulationGrowth,
    PopulationSnapshotCreate,
    PopulationSnapshotResponse,
    PopulationSnapshotUpdate,
    WeeklyDataPoint,
    YearlyCount,
)
from app.utils.pagination import paginate


class BirthService:
    """Service class for Birth CRUD and statistics operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: BirthCreate) -> Birth:
        # Create the birth record
        birth = Birth(**data.model_dump())
        self.db.add(birth)
        self.db.flush()

        # Create a Person record for the baby
        person = Person(
            first_name=data.baby_first_name,
            last_name=data.baby_last_name,
            date_of_birth=data.date_of_birth,
        )
        self.db.add(person)
        self.db.flush()  # Get person ID for relationships

        # Create parent-child relationships and add to household
        parent_ids = [
            pid for pid in [data.parent1_id, data.parent2_id] if pid is not None
        ]
        household_id = None

        for parent_id in parent_ids:
            # Parent -> Child relationship
            self.db.add(
                FamilyRelationship(
                    person_id=parent_id,
                    related_person_id=person.id,
                    relationship_type=RelationshipType.PARENT,
                )
            )
            # Child -> Parent relationship
            self.db.add(
                FamilyRelationship(
                    person_id=person.id,
                    related_person_id=parent_id,
                    relationship_type=RelationshipType.CHILD,
                )
            )

            # Find parent's primary household if we haven't found one yet
            if household_id is None:
                membership = self.db.execute(
                    select(HouseholdMember).where(
                        HouseholdMember.person_id == parent_id,
                        HouseholdMember.is_primary_household.is_(True),
                    )
                ).scalar_one_or_none()
                if membership:
                    household_id = membership.household_id

        # Add baby to parent's household as CHILD
        if household_id is not None:
            self.db.add(
                HouseholdMember(
                    household_id=household_id,
                    person_id=person.id,
                    role=HouseholdRole.CHILD,
                    is_primary_household=True,
                )
            )

        self.db.commit()
        self.db.refresh(birth)
        return birth

    def get_by_id(self, birth_id: int) -> Optional[Birth]:
        return self.db.get(Birth, birth_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        year: Optional[int] = None,
    ) -> tuple[list[Birth], int]:
        stmt = select(Birth)

        if year:
            stmt = stmt.where(extract("year", Birth.date_of_birth) == year)

        stmt = stmt.order_by(Birth.date_of_birth.desc())
        items, total = paginate(self.db, stmt, page, per_page)
        return items, total

    def update(self, birth_id: int, data: BirthUpdate) -> Optional[Birth]:
        birth = self.get_by_id(birth_id)
        if not birth:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(birth, field, value)

        self.db.commit()
        self.db.refresh(birth)
        return birth

    def delete(self, birth_id: int) -> bool:
        birth = self.get_by_id(birth_id)
        if not birth:
            return False

        self.db.delete(birth)
        self.db.commit()
        return True

    def get_birth_stats(self, year: Optional[int] = None) -> BirthStatistics:
        current_year = date.today().year

        # Get yearly counts
        stmt = (
            select(
                extract("year", Birth.date_of_birth).label("year"),
                func.count(Birth.id).label("count"),
            )
            .group_by(extract("year", Birth.date_of_birth))
            .order_by(extract("year", Birth.date_of_birth).desc())
        )

        if year:
            stmt = stmt.where(extract("year", Birth.date_of_birth) == year)

        results = self.db.execute(stmt).all()
        by_year = [YearlyCount(year=int(r.year), count=r.count) for r in results]

        total_stmt = select(func.count(Birth.id))
        if year:
            total_stmt = total_stmt.where(extract("year", Birth.date_of_birth) == year)
        total = self.db.execute(total_stmt).scalar() or 0

        return BirthStatistics(by_year=by_year, total=total, current_year=current_year)


class MassAttendanceService:
    """Service class for MassAttendance CRUD and statistics operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MassAttendanceCreate) -> MassAttendance:
        dump = data.model_dump()
        # If mass_time_id provided, resolve name for denormalized string column
        if dump.get("mass_time_id"):
            mt = self.db.get(MassTime, dump["mass_time_id"])
            if mt:
                dump["mass_time"] = mt.name
        attendance = MassAttendance(**dump)
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def get_by_id(self, attendance_id: int) -> Optional[MassAttendance]:
        stmt = (
            select(MassAttendance)
            .options(joinedload(MassAttendance.mass_time_rel))
            .where(MassAttendance.id == attendance_id)
        )
        return self.db.execute(stmt).scalars().first()

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> tuple[list[MassAttendance], int]:
        stmt = select(MassAttendance).options(joinedload(MassAttendance.mass_time_rel))

        if start_date:
            stmt = stmt.where(MassAttendance.date >= start_date)
        if end_date:
            stmt = stmt.where(MassAttendance.date <= end_date)

        stmt = stmt.order_by(MassAttendance.date.desc())
        items, total = paginate(self.db, stmt, page, per_page, unique=True)
        return items, total

    def update(
        self, attendance_id: int, data: MassAttendanceUpdate
    ) -> Optional[MassAttendance]:
        attendance = self.get_by_id(attendance_id)
        if not attendance:
            return None

        update_data = data.model_dump(exclude_unset=True)
        # If mass_time_id provided, resolve name for denormalized string column
        if "mass_time_id" in update_data and update_data["mass_time_id"]:
            mt = self.db.get(MassTime, update_data["mass_time_id"])
            if mt:
                update_data["mass_time"] = mt.name
        for field, value in update_data.items():
            setattr(attendance, field, value)

        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def delete(self, attendance_id: int) -> bool:
        attendance = self.get_by_id(attendance_id)
        if not attendance:
            return False

        self.db.delete(attendance)
        self.db.commit()
        return True

    def get_attendance_trends(
        self,
        include_breakdown: bool = False,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> AttendanceTrend | AttendanceTrendExtended:
        today = date.today()
        range_end = end_date or today
        range_start = start_date or (today - timedelta(weeks=4))
        one_year_ago = today - timedelta(days=365)
        two_years_ago = today - timedelta(days=730)

        # Recent 4 weeks data
        recent_stmt = (
            select(MassAttendance)
            .where(MassAttendance.date >= range_start)
            .where(MassAttendance.date <= range_end)
            .order_by(MassAttendance.date.desc())
        )
        recent_records = list(self.db.execute(recent_stmt).scalars().all())

        # Calculate weekly average based on actual date range
        weekly_total = sum(r.attendance_count for r in recent_records)
        num_weeks = max(((range_end - range_start).days / 7), 1)
        weekly_average = weekly_total / num_weeks if recent_records else 0.0

        # Calculate monthly average (last 12 months)
        monthly_stmt = select(func.avg(MassAttendance.attendance_count)).where(
            MassAttendance.date >= one_year_ago
        )
        monthly_average = self.db.execute(monthly_stmt).scalar() or 0.0

        # Calculate YoY change
        current_year_avg_stmt = select(func.avg(MassAttendance.attendance_count)).where(
            MassAttendance.date >= one_year_ago
        )
        current_year_avg = self.db.execute(current_year_avg_stmt).scalar() or 0

        prev_year_avg_stmt = select(func.avg(MassAttendance.attendance_count)).where(
            MassAttendance.date >= two_years_ago,
            MassAttendance.date < one_year_ago,
        )
        prev_year_avg = self.db.execute(prev_year_avg_stmt).scalar() or 0

        yoy_change = None
        if prev_year_avg and prev_year_avg > 0:
            yoy_change = ((current_year_avg - prev_year_avg) / prev_year_avg) * 100

        # Aggregate by date (sum across mass times) for chart display
        date_totals: dict[str, int] = {}
        for r in recent_records:
            d = str(r.date)
            date_totals[d] = date_totals.get(d, 0) + r.attendance_count
        recent_weeks = [
            {"date": d, "count": c, "mass_time": None}
            for d, c in sorted(date_totals.items())
        ]

        if include_breakdown:
            # Group by mass_time_id (FK), falling back to string for old records
            mass_time_label = case(
                (MassTime.name.isnot(None), MassTime.name),
                (MassAttendance.mass_time.isnot(None), MassAttendance.mass_time),
                else_="Unspecified",
            )
            breakdown_stmt = (
                select(
                    MassAttendance.mass_time_id,
                    mass_time_label.label("mass_time_label"),
                    func.sum(MassAttendance.attendance_count).label("total"),
                    func.avg(MassAttendance.attendance_count).label("avg"),
                )
                .outerjoin(MassTime, MassAttendance.mass_time_id == MassTime.id)
                .where(MassAttendance.date >= range_start)
                .where(MassAttendance.date <= range_end)
                .group_by(MassAttendance.mass_time_id, mass_time_label)
            )
            breakdown_results = self.db.execute(breakdown_stmt).all()

            by_mass_time = []
            for row in breakdown_results:
                label = row.mass_time_label
                # Get recent weeks for this specific mass time
                recent_for_time = [
                    WeeklyDataPoint(date=str(r.date), count=r.attendance_count)
                    for r in recent_records
                    if (r.mass_time_id == row.mass_time_id)
                    or (
                        r.mass_time_id is None
                        and row.mass_time_id is None
                        and (r.mass_time or "Unspecified") == label
                    )
                ]

                by_mass_time.append(
                    MassTimeBreakdown(
                        mass_time=label,
                        mass_time_id=row.mass_time_id,
                        total_attendance=int(row.total),
                        weekly_average=round(float(row.avg), 1),
                        recent_weeks=recent_for_time,
                    )
                )

            return AttendanceTrendExtended(
                weekly_average=round(weekly_average, 1),
                monthly_average=round(float(monthly_average), 1),
                yoy_change_percent=round(yoy_change, 1) if yoy_change else None,
                recent_weeks=recent_weeks,
                by_mass_time=by_mass_time,
            )

        return AttendanceTrend(
            weekly_average=round(weekly_average, 1),
            monthly_average=round(float(monthly_average), 1),
            yoy_change_percent=round(yoy_change, 1) if yoy_change else None,
            recent_weeks=recent_weeks,
        )


class PopulationService:
    """Service class for PopulationSnapshot CRUD and statistics operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: PopulationSnapshotCreate) -> PopulationSnapshot:
        snapshot = PopulationSnapshot(**data.model_dump())
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_by_id(self, snapshot_id: int) -> Optional[PopulationSnapshot]:
        return self.db.get(PopulationSnapshot, snapshot_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[PopulationSnapshot], int]:
        stmt = select(PopulationSnapshot)

        stmt = stmt.order_by(PopulationSnapshot.date.desc())
        items, total = paginate(self.db, stmt, page, per_page)
        return items, total

    def update(
        self, snapshot_id: int, data: PopulationSnapshotUpdate
    ) -> Optional[PopulationSnapshot]:
        snapshot = self.get_by_id(snapshot_id)
        if not snapshot:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(snapshot, field, value)

        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def delete(self, snapshot_id: int) -> bool:
        snapshot = self.get_by_id(snapshot_id)
        if not snapshot:
            return False

        self.db.delete(snapshot)
        self.db.commit()
        return True

    def get_population_growth(self) -> PopulationGrowth:
        # Get current counts from actual tables
        current_members = self.db.execute(select(func.count(Person.id))).scalar() or 0
        current_households = (
            self.db.execute(select(func.count(Household.id))).scalar() or 0
        )

        # Get historical snapshots for the chart
        stmt = select(PopulationSnapshot).order_by(PopulationSnapshot.date.desc())
        snapshots = list(self.db.execute(stmt).scalars().all())

        history = [PopulationSnapshotResponse.model_validate(s) for s in snapshots]

        # Calculate growth from snapshots if available
        growth_percent = None
        if snapshots:
            oldest = snapshots[-1].registered_members
            if oldest > 0:
                growth_percent = ((current_members - oldest) / oldest) * 100

        return PopulationGrowth(
            history=history,
            current_members=current_members,
            current_households=current_households,
            growth_percent=round(growth_percent, 1) if growth_percent else None,
        )
