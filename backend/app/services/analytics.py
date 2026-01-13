"""Service layer for Analytics operations."""

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.analytics import Birth, MassAttendance, PopulationSnapshot
from app.schemas.analytics import (
    AttendanceTrend,
    BirthCreate,
    BirthStatistics,
    BirthUpdate,
    MassAttendanceCreate,
    MassAttendanceUpdate,
    PopulationGrowth,
    PopulationSnapshotCreate,
    PopulationSnapshotResponse,
    PopulationSnapshotUpdate,
    YearlyCount,
)


class BirthService:
    """Service class for Birth CRUD and statistics operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: BirthCreate) -> Birth:
        birth = Birth(**data.model_dump())
        self.db.add(birth)
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

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.order_by(Birth.date_of_birth.desc())
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        items = list(self.db.execute(stmt).scalars().all())
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
        attendance = MassAttendance(**data.model_dump())
        self.db.add(attendance)
        self.db.commit()
        self.db.refresh(attendance)
        return attendance

    def get_by_id(self, attendance_id: int) -> Optional[MassAttendance]:
        return self.db.get(MassAttendance, attendance_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> tuple[list[MassAttendance], int]:
        stmt = select(MassAttendance)

        if start_date:
            stmt = stmt.where(MassAttendance.date >= start_date)
        if end_date:
            stmt = stmt.where(MassAttendance.date <= end_date)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.order_by(MassAttendance.date.desc())
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(
        self, attendance_id: int, data: MassAttendanceUpdate
    ) -> Optional[MassAttendance]:
        attendance = self.get_by_id(attendance_id)
        if not attendance:
            return None

        update_data = data.model_dump(exclude_unset=True)
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

    def get_attendance_trends(self) -> AttendanceTrend:
        today = date.today()
        four_weeks_ago = today - timedelta(weeks=4)
        one_year_ago = today - timedelta(days=365)
        two_years_ago = today - timedelta(days=730)

        # Recent 4 weeks data
        recent_stmt = (
            select(MassAttendance)
            .where(MassAttendance.date >= four_weeks_ago)
            .order_by(MassAttendance.date.desc())
        )
        recent_records = list(self.db.execute(recent_stmt).scalars().all())

        # Calculate weekly average (last 4 weeks)
        weekly_total = sum(r.attendance_count for r in recent_records)
        weekly_average = weekly_total / 4 if recent_records else 0.0

        # Calculate monthly average (last 12 months)
        monthly_stmt = select(func.avg(MassAttendance.attendance_count)).where(
            MassAttendance.date >= one_year_ago
        )
        monthly_average = self.db.execute(monthly_stmt).scalar() or 0.0

        # Calculate YoY change
        current_year_avg_stmt = select(
            func.avg(MassAttendance.attendance_count)
        ).where(MassAttendance.date >= one_year_ago)
        current_year_avg = self.db.execute(current_year_avg_stmt).scalar() or 0

        prev_year_avg_stmt = select(func.avg(MassAttendance.attendance_count)).where(
            MassAttendance.date >= two_years_ago,
            MassAttendance.date < one_year_ago,
        )
        prev_year_avg = self.db.execute(prev_year_avg_stmt).scalar() or 0

        yoy_change = None
        if prev_year_avg and prev_year_avg > 0:
            yoy_change = ((current_year_avg - prev_year_avg) / prev_year_avg) * 100

        recent_weeks = [
            {
                "date": str(r.date),
                "count": r.attendance_count,
                "mass_time": r.mass_time,
            }
            for r in recent_records[:8]
        ]

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

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.order_by(PopulationSnapshot.date.desc())
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        items = list(self.db.execute(stmt).scalars().all())
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
        # Get all snapshots ordered by date
        stmt = select(PopulationSnapshot).order_by(PopulationSnapshot.date.desc())
        snapshots = list(self.db.execute(stmt).scalars().all())

        history = [PopulationSnapshotResponse.model_validate(s) for s in snapshots]

        current_members = snapshots[0].registered_members if snapshots else 0
        current_households = snapshots[0].households if snapshots else 0

        growth_percent = None
        if len(snapshots) >= 2:
            oldest = snapshots[-1].registered_members
            if oldest > 0:
                growth_percent = ((current_members - oldest) / oldest) * 100

        return PopulationGrowth(
            history=history,
            current_members=current_members,
            current_households=current_households,
            growth_percent=round(growth_percent, 1) if growth_percent else None,
        )
