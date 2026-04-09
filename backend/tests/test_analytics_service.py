"""Unit tests for AnalyticsService: BirthService, MassAttendanceService, PopulationService."""

from datetime import date

import pytest

from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.mass_times import MassTime
from app.models.person import Person
from app.models.relationship import RelationshipType
from app.schemas.analytics import (
    BirthCreate,
    BirthUpdate,
    MassAttendanceCreate,
    MassAttendanceUpdate,
    PopulationSnapshotCreate,
    PopulationSnapshotUpdate,
)
from app.services.analytics import (
    BirthService,
    MassAttendanceService,
    PopulationService,
)


# ─── BirthService ────────────────────────────────────────────────────────────


@pytest.fixture
def parents(db_session):
    """Create two parent Persons."""
    p1 = Person(first_name="Alice", last_name="Smith", date_of_birth=date(1985, 1, 1))
    p2 = Person(first_name="Bob", last_name="Smith", date_of_birth=date(1983, 5, 10))
    db_session.add_all([p1, p2])
    db_session.flush()
    return p1, p2


@pytest.fixture
def household_with_parents(db_session, parents):
    """Create a household and add parents as members."""
    p1, p2 = parents
    hh = Household(name="Smith Family", address_line1="123 Main St", city="Auckland")
    db_session.add(hh)
    db_session.flush()
    db_session.add(
        HouseholdMember(
            household_id=hh.id,
            person_id=p1.id,
            role=HouseholdRole.HEAD,
            is_primary_household=True,
        )
    )
    db_session.add(
        HouseholdMember(
            household_id=hh.id,
            person_id=p2.id,
            role=HouseholdRole.SPOUSE,
            is_primary_household=True,
        )
    )
    db_session.commit()
    return hh


class TestBirthServiceCreate:
    def test_create_birth(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        data = BirthCreate(
            baby_first_name="Charlie",
            baby_last_name="Smith",
            date_of_birth=date(2024, 1, 15),
            parent1_id=p1.id,
        )
        result = svc.create(data)
        assert result.baby_first_name == "Charlie"
        assert result.parent1_id == p1.id

    def test_create_birth_creates_person(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        data = BirthCreate(
            baby_first_name="Charlie",
            baby_last_name="Smith",
            date_of_birth=date(2024, 1, 15),
            parent1_id=p1.id,
        )
        svc.create(data)
        # Baby Person record created
        person = db_session.query(Person).filter_by(first_name="Charlie").first()
        assert person is not None
        assert person.date_of_birth == date(2024, 1, 15)

    def test_create_birth_creates_relationships(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        svc.create(
            BirthCreate(
                baby_first_name="Charlie",
                baby_last_name="Smith",
                date_of_birth=date(2024, 1, 15),
                parent1_id=p1.id,
            )
        )
        baby = db_session.query(Person).filter_by(first_name="Charlie").first()
        from app.repositories.relationship import SqlAlchemyRelationshipRepository
        from app.services.relationship import FamilyRelationshipService

        rel_svc = FamilyRelationshipService(
            SqlAlchemyRelationshipRepository(db_session)
        )
        rel = rel_svc.get_relationship_between(p1.id, baby.id)
        assert rel is not None
        assert rel.relationship_type == RelationshipType.PARENT
        inv = rel_svc.get_relationship_between(baby.id, p1.id)
        assert inv.relationship_type == RelationshipType.CHILD

    def test_create_birth_adds_to_parent_household(
        self, db_session, household_with_parents
    ):
        svc = BirthService(db_session)
        p1 = household_with_parents.members[0].person
        svc.create(
            BirthCreate(
                baby_first_name="Charlie",
                baby_last_name="Smith",
                date_of_birth=date(2024, 1, 15),
                parent1_id=p1.id,
            )
        )
        baby = db_session.query(Person).filter_by(first_name="Charlie").first()
        member = db_session.query(HouseholdMember).filter_by(person_id=baby.id).first()
        assert member is not None
        assert member.household_id == household_with_parents.id
        assert member.role == HouseholdRole.CHILD


class TestBirthServiceGetList:
    def test_get_list_empty(self, db_session):
        svc = BirthService(db_session)
        items, total = svc.get_list()
        assert items == []
        assert total == 0

    def test_get_list_with_records(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        svc.create(
            BirthCreate(
                baby_first_name="A",
                baby_last_name="B",
                date_of_birth=date(2024, 6, 1),
                parent1_id=p1.id,
            )
        )
        svc.create(
            BirthCreate(
                baby_first_name="C",
                baby_last_name="D",
                date_of_birth=date(2023, 1, 1),
                parent1_id=p1.id,
            )
        )
        items, total = svc.get_list()
        assert total == 2
        assert len(items) == 2

    def test_get_list_filter_by_year(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        svc.create(
            BirthCreate(
                baby_first_name="A",
                baby_last_name="B",
                date_of_birth=date(2024, 1, 1),
                parent1_id=p1.id,
            )
        )
        svc.create(
            BirthCreate(
                baby_first_name="C",
                baby_last_name="D",
                date_of_birth=date(2023, 1, 1),
                parent1_id=p1.id,
            )
        )
        items, total = svc.get_list(year=2024)
        assert total == 1
        assert items[0].baby_first_name == "A"


class TestBirthServiceUpdate:
    def test_update_birth(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        birth = svc.create(
            BirthCreate(
                baby_first_name="A",
                baby_last_name="B",
                date_of_birth=date(2024, 1, 1),
                parent1_id=p1.id,
            )
        )
        result = svc.update(birth.id, BirthUpdate(place_of_birth="New Hospital"))
        assert result is not None
        assert result.place_of_birth == "New Hospital"

    def test_update_not_found(self, db_session):
        svc = BirthService(db_session)
        assert svc.update(9999, BirthUpdate(place_of_birth="X")) is None


class TestBirthServiceDelete:
    def test_delete_birth(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        birth = svc.create(
            BirthCreate(
                baby_first_name="A",
                baby_last_name="B",
                date_of_birth=date(2024, 1, 1),
                parent1_id=p1.id,
            )
        )
        assert svc.delete(birth.id) is True
        assert svc.get_by_id(birth.id) is None

    def test_delete_not_found(self, db_session):
        svc = BirthService(db_session)
        assert svc.delete(9999) is False


class TestBirthServiceStatistics:
    def test_stats_empty(self, db_session):
        svc = BirthService(db_session)
        stats = svc.get_birth_stats()
        assert stats.total == 0
        assert stats.by_year == []

    def test_stats_with_records(self, db_session, parents):
        p1, _ = parents
        svc = BirthService(db_session)
        svc.create(
            BirthCreate(
                baby_first_name="A",
                baby_last_name="B",
                date_of_birth=date(2024, 1, 1),
                parent1_id=p1.id,
            )
        )
        stats = svc.get_birth_stats()
        assert stats.total == 1
        assert any(y.year == 2024 for y in stats.by_year)


# ─── MassAttendanceService ───────────────────────────────────────────────────


@pytest.fixture
def mass_time(db_session):
    from datetime import time as dt_time

    mt = MassTime(name="Sunday 9am", day_of_week=0, time=dt_time(9, 0))
    db_session.add(mt)
    db_session.flush()
    return mt


class TestMassAttendanceServiceCreate:
    def test_create_attendance(self, db_session, mass_time):
        svc = MassAttendanceService(db_session)
        data = MassAttendanceCreate(
            mass_time_id=mass_time.id,
            date=date(2024, 1, 7),
            attendance_count=150,
        )
        result = svc.create(data)
        assert result.attendance_count == 150
        assert result.mass_time == "Sunday 9am"

    def test_create_attendance_without_mass_time(self, db_session):
        svc = MassAttendanceService(db_session)
        data = MassAttendanceCreate(
            mass_time="Custom Service", date=date(2024, 1, 7), attendance_count=80
        )
        result = svc.create(data)
        assert result.attendance_count == 80
        assert result.mass_time == "Custom Service"


class TestMassAttendanceServiceGetList:
    def test_get_list_empty(self, db_session):
        svc = MassAttendanceService(db_session)
        items, total = svc.get_list()
        assert items == []
        assert total == 0

    def test_get_list_with_records(self, db_session, mass_time):
        svc = MassAttendanceService(db_session)
        svc.create(
            MassAttendanceCreate(
                mass_time_id=mass_time.id, date=date(2024, 1, 7), attendance_count=100
            )
        )
        items, total = svc.get_list()
        assert total == 1

    def test_get_list_date_range_filter(self, db_session, mass_time):
        svc = MassAttendanceService(db_session)
        svc.create(
            MassAttendanceCreate(
                mass_time_id=mass_time.id, date=date(2024, 1, 7), attendance_count=100
            )
        )
        svc.create(
            MassAttendanceCreate(
                mass_time_id=mass_time.id, date=date(2024, 6, 7), attendance_count=120
            )
        )
        items, total = svc.get_list(
            start_date=date(2024, 6, 1), end_date=date(2024, 6, 30)
        )
        assert total == 1


class TestMassAttendanceServiceUpdate:
    def test_update_attendance(self, db_session, mass_time):
        svc = MassAttendanceService(db_session)
        rec = svc.create(
            MassAttendanceCreate(
                mass_time_id=mass_time.id, date=date(2024, 1, 7), attendance_count=100
            )
        )
        result = svc.update(rec.id, MassAttendanceUpdate(attendance_count=200))
        assert result is not None
        assert result.attendance_count == 200

    def test_update_not_found(self, db_session):
        svc = MassAttendanceService(db_session)
        assert svc.update(9999, MassAttendanceUpdate(attendance_count=1)) is None


class TestMassAttendanceServiceDelete:
    def test_delete_attendance(self, db_session, mass_time):
        svc = MassAttendanceService(db_session)
        rec = svc.create(
            MassAttendanceCreate(
                mass_time_id=mass_time.id, date=date(2024, 1, 7), attendance_count=100
            )
        )
        assert svc.delete(rec.id) is True
        assert svc.get_by_id(rec.id) is None

    def test_delete_not_found(self, db_session):
        svc = MassAttendanceService(db_session)
        assert svc.delete(9999) is False


# ─── PopulationService ──────────────────────────────────────────────────────


class TestPopulationService:
    def test_create_snapshot(self, db_session):
        svc = PopulationService(db_session)
        data = PopulationSnapshotCreate(
            date=date(2024, 1, 1),
            registered_members=100,
            active_households=50,
            weekly_attendance=300,
        )
        result = svc.create(data)
        assert result.registered_members == 100

    def test_get_by_id(self, db_session):
        svc = PopulationService(db_session)
        snap = svc.create(
            PopulationSnapshotCreate(
                date=date(2024, 1, 1), registered_members=100, active_households=50
            )
        )
        result = svc.get_by_id(snap.id)
        assert result is not None
        assert result.id == snap.id

    def test_get_by_id_not_found(self, db_session):
        svc = PopulationService(db_session)
        assert svc.get_by_id(9999) is None

    def test_get_list(self, db_session):
        svc = PopulationService(db_session)
        svc.create(
            PopulationSnapshotCreate(
                date=date(2024, 1, 1), registered_members=100, active_households=50
            )
        )
        svc.create(
            PopulationSnapshotCreate(
                date=date(2023, 1, 1), registered_members=80, active_households=40
            )
        )
        items, total = svc.get_list()
        assert total == 2
        # Ordered by date desc
        assert items[0].date > items[1].date

    def test_update(self, db_session):
        svc = PopulationService(db_session)
        snap = svc.create(
            PopulationSnapshotCreate(
                date=date(2024, 1, 1), registered_members=100, active_households=50
            )
        )
        result = svc.update(snap.id, PopulationSnapshotUpdate(registered_members=105))
        assert result is not None
        assert result.registered_members == 105

    def test_update_not_found(self, db_session):
        svc = PopulationService(db_session)
        assert svc.update(9999, PopulationSnapshotUpdate(registered_members=1)) is None

    def test_delete(self, db_session):
        svc = PopulationService(db_session)
        snap = svc.create(
            PopulationSnapshotCreate(
                date=date(2024, 1, 1), registered_members=100, active_households=50
            )
        )
        assert svc.delete(snap.id) is True
        assert svc.get_by_id(snap.id) is None

    def test_delete_not_found(self, db_session):
        svc = PopulationService(db_session)
        assert svc.delete(9999) is False

    def test_get_population_growth_empty(self, db_session):
        svc = PopulationService(db_session)
        growth = svc.get_population_growth()
        assert growth.current_members == 0
        assert growth.current_households == 0
        assert growth.growth_percent is None

    def test_get_population_growth_with_data(self, db_session):
        svc = PopulationService(db_session)
        # Add a person
        svc.db.add(Person(first_name="A", last_name="B"))
        svc.db.flush()
        # Add an old snapshot
        svc.create(
            PopulationSnapshotCreate(
                date=date(2020, 1, 1), registered_members=1, active_households=1
            )
        )
        growth = svc.get_population_growth()
        # Growth should be calculable from snapshot
        assert growth is not None
