"""Unit tests for PersonService."""

from datetime import date

from app.models.person import Gender
from app.schemas.filters import PersonFilter
from app.schemas.person import PersonCreate, PersonUpdate
from app.repositories.person import SqlAlchemyPersonRepository
from app.services.person import PersonService


class TestPersonServiceCreate:
    """Tests for PersonService.create method."""

    def test_create_person_with_minimal_data(self, db_session):
        """Test creating a person with only required fields."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))
        person_data = PersonCreate(first_name="John", last_name="Smith")

        person = service.create(person_data)

        assert person.id is not None
        assert person.first_name == "John"
        assert person.last_name == "Smith"
        assert person.email is None
        assert person.created_at is not None

    def test_create_person_with_full_data(self, db_session):
        """Test creating a person with all fields."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))
        person_data = PersonCreate(
            first_name="John",
            middle_name="Michael",
            last_name="Smith",
            date_of_birth=date(1985, 3, 15),
            gender=Gender.MALE,
            email="john@test.com",
            phone="+64 21 123 4567",
            address_line1="123 Main Street",
            city="Auckland",
            postal_code="1010",
            notes="Test notes",
        )

        person = service.create(person_data)

        assert person.id is not None
        assert person.first_name == "John"
        assert person.middle_name == "Michael"
        assert person.last_name == "Smith"
        assert person.date_of_birth == date(1985, 3, 15)
        assert person.gender == Gender.MALE
        assert person.email == "john@test.com"
        assert person.phone == "+64 21 123 4567"
        assert person.address_line1 == "123 Main Street"
        assert person.city == "Auckland"
        assert person.postal_code == "1010"
        assert person.notes == "Test notes"


class TestPersonServiceGetById:
    """Tests for PersonService.get_by_id method."""

    def test_get_existing_person(self, db_session, sample_person):
        """Test getting an existing person by ID."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        person = service.get_by_id(sample_person.id)

        assert person is not None
        assert person.id == sample_person.id
        assert person.first_name == sample_person.first_name

    def test_get_nonexistent_person(self, db_session):
        """Test getting a person that doesn't exist."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        person = service.get_by_id(9999)

        assert person is None


class TestPersonServiceGetByIdWithRelations:
    """Tests for PersonService.get_by_id_with_relations method."""

    def test_get_person_with_relations(self, db_session, sample_person):
        """Test getting a person with related data."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        person = service.get_by_id_with_relations(sample_person.id)

        assert person is not None
        assert person.id == sample_person.id
        assert hasattr(person, "household_memberships")
        assert hasattr(person, "sacraments")

    def test_get_nonexistent_person_with_relations(self, db_session):
        """Test getting a nonexistent person with relations."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        person = service.get_by_id_with_relations(9999)

        assert person is None


class TestPersonServiceGetList:
    """Tests for PersonService.get_list method."""

    def test_get_list_empty(self, db_session):
        """Test getting list when no persons exist."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, total = service.get_list(filters=PersonFilter())

        assert items == []
        assert total == 0

    def test_get_list_with_persons(self, db_session, multiple_persons):
        """Test getting list with persons."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, total = service.get_list(filters=PersonFilter())

        assert len(items) == 5
        assert total == 5

    def test_get_list_pagination(self, db_session, multiple_persons):
        """Test pagination works correctly."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, total = service.get_list(filters=PersonFilter(), page=1, per_page=2)

        assert len(items) == 2
        assert total == 5

        items_page2, _ = service.get_list(filters=PersonFilter(), page=2, per_page=2)
        assert len(items_page2) == 2

    def test_get_list_search(self, db_session, multiple_persons):
        """Test search functionality."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, total = service.get_list(filters=PersonFilter(search="Alice"))

        assert len(items) == 1
        assert items[0].first_name == "Alice"

    def test_get_list_search_by_email(self, db_session, multiple_persons):
        """Test search by email."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, total = service.get_list(filters=PersonFilter(search="bob@test"))

        assert len(items) == 1
        assert items[0].first_name == "Bob"

    def test_get_list_filter_by_gender(self, db_session, multiple_persons):
        """Test filtering by gender."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, total = service.get_list(filters=PersonFilter(gender=Gender.FEMALE))

        assert total == 3
        for person in items:
            assert person.gender == Gender.FEMALE

    def test_get_list_sorting_asc(self, db_session, multiple_persons):
        """Test ascending sort."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, _ = service.get_list(
            filters=PersonFilter(), sort_by="last_name", sort_order="asc"
        )

        assert items[0].last_name == "Anderson"
        assert items[-1].last_name == "Evans"

    def test_get_list_sorting_desc(self, db_session, multiple_persons):
        """Test descending sort."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        items, _ = service.get_list(
            filters=PersonFilter(), sort_by="last_name", sort_order="desc"
        )

        assert items[0].last_name == "Evans"
        assert items[-1].last_name == "Anderson"


class TestPersonServiceUpdate:
    """Tests for PersonService.update method."""

    def test_update_person_partial(self, db_session, sample_person):
        """Test partial update of a person."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))
        update_data = PersonUpdate(first_name="Jane")

        updated = service.update(sample_person.id, update_data)

        assert updated is not None
        assert updated.first_name == "Jane"
        assert updated.last_name == sample_person.last_name

    def test_update_person_full(self, db_session, sample_person):
        """Test full update of a person."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))
        update_data = PersonUpdate(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@test.com",
        )

        updated = service.update(sample_person.id, update_data)

        assert updated is not None
        assert updated.first_name == "Jane"
        assert updated.last_name == "Doe"
        assert updated.email == "jane.doe@test.com"

    def test_update_nonexistent_person(self, db_session):
        """Test updating a person that doesn't exist."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))
        update_data = PersonUpdate(first_name="Jane")

        updated = service.update(9999, update_data)

        assert updated is None


class TestPersonServiceDelete:
    """Tests for PersonService.delete method."""

    def test_delete_person(self, db_session, sample_person):
        """Test deleting a person."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))
        person_id = sample_person.id

        deleted = service.delete(person_id)

        assert deleted is True
        assert service.get_by_id(person_id) is None

    def test_delete_nonexistent_person(self, db_session):
        """Test deleting a person that doesn't exist."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        deleted = service.delete(9999)

        assert deleted is False


class TestPersonServiceGetByEmail:
    """Tests for PersonService.get_by_email method."""

    def test_get_by_email_existing(self, db_session, sample_person):
        """Test getting a person by existing email."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        person = service.get_by_email(sample_person.email)

        assert person is not None
        assert person.id == sample_person.id

    def test_get_by_email_nonexistent(self, db_session):
        """Test getting a person by nonexistent email."""
        service = PersonService(SqlAlchemyPersonRepository(db_session))

        person = service.get_by_email("nonexistent@test.com")

        assert person is None
