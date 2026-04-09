"""Unit tests for MassTimeService (#172)."""

from datetime import time

import pytest

from app.models.mass_times import MassTime
from app.repositories.mass_time import SqlAlchemyMassTimeRepository
from app.schemas.mass_times import MassTimeCreate, MassTimeUpdate
from app.services.mass_times import MassTimeService


@pytest.fixture
def sample_mass_time(db_session):
    mt = MassTime(
        name="Sunday Morning",
        time=time(9, 0),
        is_active=True,
    )
    db_session.add(mt)
    db_session.commit()
    db_session.refresh(mt)
    return mt


class TestMassTimeServiceCreate:
    def test_create_mass_time(self, db_session):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        data = MassTimeCreate(
            name="Sunday Morning",
            time=time(9, 0),
        )
        result = svc.create(data)
        assert result.name == "Sunday Morning"
        assert result.time == time(9, 0)


class TestMassTimeServiceGetList:
    def test_get_list_empty(self, db_session):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        assert svc.get_list() == []

    def test_get_list_with_records(self, db_session, sample_mass_time):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        results = svc.get_list()
        assert len(results) == 1
        assert results[0].name == "Sunday Morning"

    def test_get_list_active_only(self, db_session, sample_mass_time):
        sample_mass_time.is_active = False
        db_session.commit()
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        active = svc.get_list(active_only=True)
        assert len(active) == 0
        all_mt = svc.get_list(active_only=False)
        assert len(all_mt) == 1


class TestMassTimeServiceGetById:
    def test_get_existing(self, db_session, sample_mass_time):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        result = svc.get_by_id(sample_mass_time.id)
        assert result is not None
        assert result.id == sample_mass_time.id

    def test_get_not_found(self, db_session):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        assert svc.get_by_id(9999) is None


class TestMassTimeServiceUpdate:
    def test_update_mass_time(self, db_session, sample_mass_time):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        data = MassTimeUpdate(location="New Location")
        result = svc.update(sample_mass_time.id, data)
        assert result is not None
        assert result.location == "New Location"

    def test_update_not_found(self, db_session):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        assert svc.update(9999, MassTimeUpdate(name="X")) is None


class TestMassTimeServiceDelete:
    def test_delete_deactivates(self, db_session, sample_mass_time):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        assert svc.delete(sample_mass_time.id) is True
        # Soft-delete: is_active set to False
        result = svc.get_by_id(sample_mass_time.id)
        assert result is not None
        assert result.is_active is False

    def test_delete_not_found(self, db_session):
        svc = MassTimeService(SqlAlchemyMassTimeRepository(db_session))
        assert svc.delete(9999) is False
