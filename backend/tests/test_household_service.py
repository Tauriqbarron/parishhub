"""Unit tests for HouseholdService edge cases."""

from datetime import date

import pytest

from app.models.household import Household, HouseholdRole
from app.models.person import Gender, Person
from app.repositories.household import SqlAlchemyHouseholdRepository
from app.schemas.household import HouseholdCreate, HouseholdMemberCreate
from app.services.household import HouseholdService


@pytest.fixture
def sample_household(db_session):
    """Create a sample household."""
    household = Household(
        name="The Smith Family",
        address_line1="123 Main Street",
        city="Auckland",
    )
    db_session.add(household)
    db_session.commit()
    return household


@pytest.fixture
def sample_person(db_session):
    """Create a sample person."""
    person = Person(
        first_name="John",
        last_name="Smith",
        gender=Gender.MALE,
        date_of_birth=date(1985, 3, 15),
    )
    db_session.add(person)
    db_session.commit()
    return person


class TestHouseholdServiceGetById:
    """Tests for HouseholdService.get_by_id edge cases."""

    def test_get_by_id_exists(self, db_session, sample_household):
        """Test getting an existing household by ID."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        result = svc.get_by_id(sample_household.id)
        assert result is not None
        assert result.id == sample_household.id
        assert result.name == "The Smith Family"

    def test_get_by_id_not_found(self, db_session):
        """Test getting a non-existent household returns None."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        result = svc.get_by_id(9999)
        assert result is None


class TestHouseholdServiceGetList:
    """Tests for HouseholdService.get_list edge cases."""

    def test_get_list_desc_sort(self, db_session):
        """Test get_list with descending sort order."""
        # Create multiple households
        households = [
            Household(name="Alpha Family"),
            Household(name="Beta Family"),
            Household(name="Gamma Family"),
        ]
        for h in households:
            db_session.add(h)
        db_session.commit()

        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        items, total = svc.get_list(sort_by="name", sort_order="desc")

        assert total == 3
        assert len(items) == 3
        # Verify descending order
        assert items[0].name == "Gamma Family"
        assert items[1].name == "Beta Family"
        assert items[2].name == "Alpha Family"

    def test_get_list_asc_sort(self, db_session):
        """Test get_list with ascending sort order."""
        households = [
            Household(name="Zeta Family"),
            Household(name="Alpha Family"),
        ]
        for h in households:
            db_session.add(h)
        db_session.commit()

        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        items, total = svc.get_list(sort_by="name", sort_order="asc")

        assert total == 2
        assert items[0].name == "Alpha Family"
        assert items[1].name == "Zeta Family"

    def test_get_list_pagination(self, db_session):
        """Test get_list pagination."""
        for i in range(5):
            db_session.add(Household(name=f"Family {i}"))
        db_session.commit()

        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        items, total = svc.get_list(page=1, per_page=2)

        assert total == 5
        assert len(items) == 2

    def test_get_list_search(self, db_session):
        """Test get_list search functionality."""
        db_session.add_all(
            [
                Household(name="Smith Family"),
                Household(name="Jones Family"),
                Household(name="Smithson Family"),
            ]
        )
        db_session.commit()

        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        items, total = svc.get_list(search="Smith")

        assert total == 2  # Smith Family and Smithson Family
        names = {h.name for h in items}
        assert "Smith Family" in names
        assert "Smithson Family" in names


class TestHouseholdServiceAddMember:
    """Tests for HouseholdService.add_member edge cases."""

    def test_add_member_person_not_exists(self, db_session, sample_household):
        """Test adding a member with non-existent person returns None."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        data = HouseholdMemberCreate(
            household_id=sample_household.id,
            person_id=9999,  # Non-existent person
            role=HouseholdRole.HEAD,
        )
        result = svc.add_member(data)
        assert result is None

    def test_add_member_existing_member(
        self, db_session, sample_household, sample_person
    ):
        """Test adding a person who is already a member returns None."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)

        # Add member first time
        data = HouseholdMemberCreate(
            household_id=sample_household.id,
            person_id=sample_person.id,
            role=HouseholdRole.HEAD,
        )
        result1 = svc.add_member(data)
        assert result1 is not None

        # Try to add same person again
        data2 = HouseholdMemberCreate(
            household_id=sample_household.id,
            person_id=sample_person.id,
            role=HouseholdRole.SPOUSE,  # Different role
        )
        result2 = svc.add_member(data2)
        assert result2 is None  # Should fail because person is already a member

    def test_add_member_household_not_exists(self, db_session, sample_person):
        """Test adding a member to non-existent household returns None."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        data = HouseholdMemberCreate(
            household_id=9999,  # Non-existent household
            person_id=sample_person.id,
            role=HouseholdRole.HEAD,
        )
        result = svc.add_member(data)
        assert result is None

    def test_add_member_success(self, db_session, sample_household, sample_person):
        """Test successfully adding a member."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        data = HouseholdMemberCreate(
            household_id=sample_household.id,
            person_id=sample_person.id,
            role=HouseholdRole.HEAD,
            is_primary_household=True,
        )
        result = svc.add_member(data)
        assert result is not None
        assert result.person_id == sample_person.id
        assert result.household_id == sample_household.id
        assert result.role == HouseholdRole.HEAD
        assert result.is_primary_household is True


class TestHouseholdServiceGetMemberCount:
    """Tests for HouseholdService.get_member_count."""

    def test_get_member_count_empty(self, db_session, sample_household):
        """Test getting member count for household with no members."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        count = svc.get_member_count(sample_household.id)
        assert count == 0

    def test_get_member_count_with_members(self, db_session, sample_household):
        """Test getting member count with multiple members."""
        # Create multiple people and add them to household
        people = [
            Person(first_name="John", last_name="Smith"),
            Person(first_name="Jane", last_name="Smith"),
            Person(first_name="Junior", last_name="Smith"),
        ]
        for p in people:
            db_session.add(p)
        db_session.flush()

        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        for i, person in enumerate(people):
            role = HouseholdRole.HEAD if i == 0 else HouseholdRole.CHILD
            data = HouseholdMemberCreate(
                household_id=sample_household.id,
                person_id=person.id,
                role=role,
            )
            svc.add_member(data)

        count = svc.get_member_count(sample_household.id)
        assert count == 3

    def test_get_member_count_nonexistent_household(self, db_session):
        """Test getting member count for non-existent household."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        count = svc.get_member_count(9999)
        assert count == 0


class TestHouseholdServiceOtherMethods:
    """Tests for other HouseholdService methods."""

    def test_create_household(self, db_session):
        """Test creating a household."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        data = HouseholdCreate(
            name="New Family",
            address_line1="456 Oak Avenue",
            city="Wellington",
        )
        result = svc.create(data)
        assert result is not None
        assert result.name == "New Family"
        assert result.address_line1 == "456 Oak Avenue"

    def test_get_by_id_with_members(self, db_session, sample_household, sample_person):
        """Test getting household with members."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)

        # Add a member
        member_data = HouseholdMemberCreate(
            household_id=sample_household.id,
            person_id=sample_person.id,
            role=HouseholdRole.HEAD,
        )
        svc.add_member(member_data)

        result = svc.get_by_id_with_members(sample_household.id)
        assert result is not None
        assert len(result.members) == 1
        assert result.members[0].person_id == sample_person.id

    def test_delete_household(self, db_session, sample_household):
        """Test deleting a household."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        result = svc.delete(sample_household.id)
        assert result is True

        # Verify it's deleted
        assert svc.get_by_id(sample_household.id) is None

    def test_delete_nonexistent_household(self, db_session):
        """Test deleting a non-existent household returns False."""
        svc = HouseholdService(SqlAlchemyHouseholdRepository(db_session), db_session)
        result = svc.delete(9999)
        assert result is False
