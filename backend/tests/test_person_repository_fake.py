"""Tests for FakePersonRepository in-memory implementation."""

from sqlalchemy import select

from app.models.person import Person
from app.repositories.person import FakePersonRepository


def _make_person(
    person_id=None, first_name="John", last_name="Smith", email=None, dob=None
):
    """Helper to create a Person instance without DB."""
    p = Person(
        first_name=first_name, last_name=last_name, email=email, date_of_birth=dob
    )
    p.id = person_id
    return p


class TestFakePersonRepositoryInit:
    """Tests for FakePersonRepository.__init__ with pre-populated persons."""

    def test_empty_init(self):
        repo = FakePersonRepository()
        assert repo._persons == {}
        assert repo._next_id == 1

    def test_init_with_persons(self):
        p1 = _make_person(person_id=5, first_name="Alice")
        p2 = _make_person(person_id=10, first_name="Bob")
        repo = FakePersonRepository(persons=[p1, p2])
        assert 5 in repo._persons
        assert 10 in repo._persons
        assert repo._next_id == 11

    def test_init_with_none_list(self):
        repo = FakePersonRepository(persons=None)
        assert repo._persons == {}


class TestFakePersonRepositoryGetById:
    """Tests for FakePersonRepository.get_by_id."""

    def test_get_existing(self):
        p = _make_person(person_id=1, first_name="Alice")
        repo = FakePersonRepository(persons=[p])
        assert repo.get_by_id(1) is p

    def test_get_nonexistent(self):
        repo = FakePersonRepository()
        assert repo.get_by_id(999) is None


class TestFakePersonRepositoryGetByEmail:
    """Tests for FakePersonRepository.get_by_email."""

    def test_get_by_email_match(self):
        p = _make_person(person_id=1, email="alice@test.com")
        repo = FakePersonRepository(persons=[p])
        assert repo.get_by_email("alice@test.com") is p

    def test_get_by_email_no_match(self):
        p = _make_person(person_id=1, email="alice@test.com")
        repo = FakePersonRepository(persons=[p])
        assert repo.get_by_email("bob@test.com") is None

    def test_get_by_email_none_email(self):
        p = _make_person(person_id=1, email=None)
        repo = FakePersonRepository(persons=[p])
        assert repo.get_by_email("any@test.com") is None


class TestFakePersonRepositoryGetByIdWithRelations:
    """Tests for FakePersonRepository.get_by_id_with_relations."""

    def test_returns_person(self):
        p = _make_person(person_id=1)
        repo = FakePersonRepository(persons=[p])
        assert repo.get_by_id_with_relations(1) is p

    def test_returns_none_for_missing(self):
        repo = FakePersonRepository()
        assert repo.get_by_id_with_relations(999) is None


class TestFakePersonRepositorySave:
    """Tests for FakePersonRepository.save — auto-increment ID assignment."""

    def test_save_new_person_assigns_id(self):
        repo = FakePersonRepository()
        p = _make_person(person_id=None, first_name="New")
        saved = repo.save(p)
        assert saved.id == 1
        assert repo._persons[1] is p

    def test_save_multiple_increments(self):
        repo = FakePersonRepository()
        p1 = repo.save(_make_person(person_id=None))
        p2 = repo.save(_make_person(person_id=None))
        assert p1.id == 1
        assert p2.id == 2

    def test_save_existing_person_keeps_id(self):
        repo = FakePersonRepository()
        p = _make_person(person_id=42, first_name="Existing")
        saved = repo.save(p)
        assert saved.id == 42
        assert 42 in repo._persons

    def test_save_updates_existing(self):
        p = _make_person(person_id=1, first_name="Old")
        repo = FakePersonRepository(persons=[p])
        p.first_name = "New"
        repo.save(p)
        assert repo._persons[1].first_name == "New"


class TestFakePersonRepositoryDelete:
    """Tests for FakePersonRepository.delete."""

    def test_delete_existing(self):
        p = _make_person(person_id=1)
        repo = FakePersonRepository(persons=[p])
        repo.delete(p)
        assert 1 not in repo._persons

    def test_delete_nonexistent_no_error(self):
        repo = FakePersonRepository()
        p = _make_person(person_id=999)
        repo.delete(p)  # Should not raise


class TestFakePersonRepositoryList:
    """Tests for FakePersonRepository.list — returns all persons ignoring stmt."""

    def test_list_empty(self):
        repo = FakePersonRepository()
        result = repo.list(select(Person))
        assert result == []

    def test_list_returns_all(self):
        p1 = _make_person(person_id=1)
        p2 = _make_person(person_id=2)
        repo = FakePersonRepository(persons=[p1, p2])
        result = repo.list(select(Person))
        assert len(result) == 2


class TestFakePersonRepositoryCount:
    """Tests for FakePersonRepository.count — returns length of store."""

    def test_count_empty(self):
        repo = FakePersonRepository()
        assert repo.count(select(Person)) == 0

    def test_count_with_persons(self):
        persons = [_make_person(person_id=i) for i in range(1, 6)]
        repo = FakePersonRepository(persons=persons)
        assert repo.count(select(Person)) == 5
