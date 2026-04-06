"""Unit tests for SacramentService ordering rules."""

from datetime import date

import pytest

from app.models.person import Person
from app.models.sacrament import Sacrament, SacramentType
from app.schemas.sacrament import SacramentCreate
from app.services.sacrament import SacramentService, SacramentValidationError


@pytest.fixture
def person_with_baptism(db_session):
    """Create a person with a Baptism record."""
    person = Person(first_name="Test", last_name="Person")
    db_session.add(person)
    db_session.flush()
    sacrament = Sacrament(
        person_id=person.id,
        sacrament_type=SacramentType.BAPTISM,
        date_received=date(2000, 1, 1),
    )
    db_session.add(sacrament)
    db_session.commit()
    return person


@pytest.fixture
def person_with_communion(db_session, person_with_baptism):
    """Create a person with Baptism and First Communion."""
    sacrament = Sacrament(
        person_id=person_with_baptism.id,
        sacrament_type=SacramentType.FIRST_COMMUNION,
        date_received=date(2010, 1, 1),
    )
    db_session.add(sacrament)
    db_session.commit()
    return person_with_baptism


@pytest.fixture
def person_with_confirmation(db_session, person_with_communion):
    """Create a person with Baptism, First Communion, and Confirmation."""
    sacrament = Sacrament(
        person_id=person_with_communion.id,
        sacrament_type=SacramentType.CONFIRMATION,
        date_received=date(2015, 1, 1),
    )
    db_session.add(sacrament)
    db_session.commit()
    return person_with_communion


class TestSacramentOrdering:
    """Tests for canonical Catholic sacrament ordering rules."""

    def test_baptism_allows_first_communion_after(
        self, db_session, person_with_baptism
    ):
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_baptism.id,
            sacrament_type=SacramentType.FIRST_COMMUNION,
            date_received=date(2010, 1, 1),
        )
        result = svc.create(data)
        assert result.sacrament_type == SacramentType.FIRST_COMMUNION

    def test_first_communion_before_baptism_raises(
        self, db_session, person_with_baptism
    ):
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_baptism.id,
            sacrament_type=SacramentType.FIRST_COMMUNION,
            date_received=date(1999, 1, 1),
        )
        with pytest.raises(SacramentValidationError, match="after Baptism"):
            svc.create(data)

    def test_confirmation_requires_after_baptism(self, db_session, person_with_baptism):
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_baptism.id,
            sacrament_type=SacramentType.CONFIRMATION,
            date_received=date(1999, 1, 1),
        )
        with pytest.raises(SacramentValidationError, match="after Baptism"):
            svc.create(data)

    def test_confirmation_requires_after_first_communion(
        self, db_session, person_with_baptism
    ):
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_baptism.id,
            sacrament_type=SacramentType.CONFIRMATION,
            date_received=date(2005, 1, 1),  # after baptism but before communion
        )
        with pytest.raises(SacramentValidationError, match="after First Communion"):
            svc.create(data)

    def test_duplicate_baptism_raises(self, db_session, person_with_baptism):
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_baptism.id,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(2001, 1, 1),
        )
        with pytest.raises(SacramentValidationError, match="already has a baptism"):
            svc.create(data)

    def test_marriage_allows_duplicates(self, db_session):
        person = Person(first_name="A", last_name="B")
        db_session.add(person)
        db_session.flush()
        svc = SacramentService(db_session)
        svc.create(
            SacramentCreate(
                person_id=person.id,
                sacrament_type=SacramentType.MARRIAGE,
                date_received=date(2010, 1, 1),
            )
        )
        result = svc.create(
            SacramentCreate(
                person_id=person.id,
                sacrament_type=SacramentType.MARRIAGE,
                date_received=date(2020, 1, 1),
            )
        )
        assert result is not None

    def test_person_not_found_raises(self, db_session):
        svc = SacramentService(db_session)
        with pytest.raises(SacramentValidationError, match="not found"):
            svc.create(
                SacramentCreate(
                    person_id=9999,
                    sacrament_type=SacramentType.BAPTISM,
                    date_received=date(2000, 1, 1),
                )
            )

    def test_baptism_after_existing_communion_raises(
        self, db_session, person_with_communion
    ):
        """If Baptism is added retroactively after Communion exists, it must be earlier."""
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_communion.id,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(2011, 1, 1),  # after first communion
        )
        with pytest.raises(SacramentValidationError, match="before First Communion"):
            svc.create(data)

    def test_baptism_after_existing_confirmation_raises(
        self, db_session, person_with_confirmation
    ):
        """If Baptism is added retroactively after Confirmation exists, it must be earlier."""
        svc = SacramentService(db_session)
        data = SacramentCreate(
            person_id=person_with_confirmation.id,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(2016, 1, 1),  # after confirmation
        )
        with pytest.raises(SacramentValidationError, match="before Confirmation"):
            svc.create(data)
