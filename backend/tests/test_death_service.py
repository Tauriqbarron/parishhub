"""Unit tests for DeathService."""

from datetime import date

import pytest

from app.models.death import Death
from app.models.person import Person
from app.schemas.death import DeathCreate, DeathUpdate
from app.repositories.death import SqlAlchemyDeathRepository
from app.services.death import DeathService, DeathValidationError


@pytest.fixture
def person(db_session):
    """Create a person for death record testing."""
    p = Person(
        first_name="John",
        last_name="Smith",
        date_of_birth=date(1940, 6, 15),
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def person_without_dob(db_session):
    """Create a person without date of birth."""
    p = Person(first_name="Jane", last_name="Doe")
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def death_record(db_session, person):
    """Create a death record for testing."""
    death = Death(
        person_id=person.id,
        date_of_death=date(2020, 3, 10),
        place_of_death="St. Mary's Hospital",
    )
    db_session.add(death)
    db_session.commit()
    db_session.refresh(death)
    return death


class TestDeathServiceCreate:
    def test_create_death_record(self, db_session, person):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathCreate(person_id=person.id, date_of_death=date(2020, 3, 10))
        result = svc.create(data)
        assert result.person_id == person.id
        assert result.date_of_death == date(2020, 3, 10)
        assert result.id is not None

    def test_create_with_full_data(self, db_session, person):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathCreate(
            person_id=person.id,
            date_of_death=date(2020, 3, 10),
            place_of_death="Hospital",
            cause_of_death="Illness",
            burial_date=date(2020, 3, 15),
            burial_location="Cemetery A",
            funeral_date=date(2020, 3, 13),
            funeral_location="Church B",
            notes="Test notes",
        )
        result = svc.create(data)
        assert result.place_of_death == "Hospital"
        assert result.cause_of_death == "Illness"
        assert result.notes == "Test notes"

    def test_create_duplicate_raises(self, db_session, person, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathCreate(person_id=person.id, date_of_death=date(2021, 1, 1))
        with pytest.raises(DeathValidationError, match="already exists"):
            svc.create(data)

    def test_create_person_not_found_raises(self, db_session):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathCreate(person_id=9999, date_of_death=date(2020, 1, 1))
        with pytest.raises(DeathValidationError, match="not found"):
            svc.create(data)

    def test_create_future_date_raises(self, db_session, person):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        future = date.today().replace(year=date.today().year + 1)
        data = DeathCreate(person_id=person.id, date_of_death=future)
        with pytest.raises(DeathValidationError, match="cannot be in the future"):
            svc.create(data)

    def test_create_before_birth_raises(self, db_session, person):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathCreate(person_id=person.id, date_of_birth=date(1930, 1, 1))
        with pytest.raises(DeathValidationError, match="before date of birth"):
            svc.create(data)

    def test_create_without_person_dob_succeeds(self, db_session, person_without_dob):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathCreate(
            person_id=person_without_dob.id, date_of_death=date(2020, 1, 1)
        )
        result = svc.create(data)
        assert result.date_of_death == date(2020, 1, 1)


class TestDeathServiceGetById:
    def test_get_existing(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        result = svc.get_by_id(death_record.id)
        assert result is not None
        assert result.id == death_record.id
        assert result.person is not None
        assert result.person.first_name == "John"

    def test_get_not_found(self, db_session):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        assert svc.get_by_id(9999) is None


class TestDeathServiceGetByPersonId:
    def test_get_existing(self, db_session, death_record, person):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        result = svc.get_by_person_id(person.id)
        assert result is not None
        assert result.id == death_record.id

    def test_get_not_found(self, db_session, person_without_dob):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        assert svc.get_by_person_id(person_without_dob.id) is None


class TestDeathServiceGetList:
    def test_get_list_empty(self, db_session):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        items, total = svc.get_list()
        assert items == []
        assert total == 0

    def test_get_list_with_records(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        items, total = svc.get_list()
        assert len(items) == 1
        assert total == 1

    def test_get_list_filter_by_year(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        items, total = svc.get_list(year=2020)
        assert total == 1
        items2, total2 = svc.get_list(year=2025)
        assert total2 == 0

    def test_get_list_pagination(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        items, total = svc.get_list(page=1, per_page=1)
        assert len(items) == 1
        assert total == 1


class TestDeathServiceUpdate:
    def test_update_place_of_death(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathUpdate(place_of_death="New Hospital")
        result = svc.update(death_record.id, data)
        assert result is not None
        assert result.place_of_death == "New Hospital"

    def test_update_valid_date(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathUpdate(date_of_death=date(2021, 5, 1))
        result = svc.update(death_record.id, data)
        assert result is not None
        assert result.date_of_death == date(2021, 5, 1)

    def test_update_future_date_raises(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        future = date.today().replace(year=date.today().year + 1)
        data = DeathUpdate(date_of_death=future)
        with pytest.raises(DeathValidationError, match="cannot be in the future"):
            svc.update(death_record.id, data)

    def test_update_date_before_birth_raises(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathUpdate(date_of_death=date(1930, 1, 1))
        with pytest.raises(DeathValidationError, match="before date of birth"):
            svc.update(death_record.id, data)

    def test_update_not_found(self, db_session):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        data = DeathUpdate(place_of_death="X")
        assert svc.update(9999, data) is None


class TestDeathServiceDelete:
    def test_delete_existing(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        result = svc.delete(death_record.id)
        assert result is True
        assert svc.get_by_id(death_record.id) is None

    def test_delete_not_found(self, db_session):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        assert svc.delete(9999) is False


class TestDeathServiceStatistics:
    def test_statistics_empty(self, db_session):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        stats = svc.get_statistics()
        assert stats.total == 0
        assert stats.current_year_count == 0
        assert stats.by_year == []

    def test_statistics_with_records(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        stats = svc.get_statistics()
        assert stats.total == 1
        assert stats.current_year_count == 0  # record is from 2020
        assert len(stats.by_year) == 1
        assert stats.by_year[0].year == 2020
        assert stats.by_year[0].count == 1

    def test_statistics_filter_by_year(self, db_session, death_record):
        svc = DeathService(SqlAlchemyDeathRepository(db_session), db_session)
        stats = svc.get_statistics(year=2020)
        assert stats.total == 1
        assert stats.current_year_count == 0  # always based on current year
