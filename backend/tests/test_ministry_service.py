"""Unit tests for MinistryService using FakeMinistryRepository."""

from datetime import date

import pytest

from app.models.ministry import Ministry, MinistryMember
from app.repositories.ministry import FakeMinistryRepository
from app.schemas.ministry import (
    MinistryCreate,
    MinistryEventCreate,
    MinistryMemberCreate,
    MinistryMemberUpdate,
    MinistryUpdate,
)
from app.services.ministry import MinistryService, MinistryValidationError


@pytest.fixture
def fake_repo():
    return FakeMinistryRepository()


@pytest.fixture
def service(fake_repo, db_session):
    return MinistryService(fake_repo, db_session)


@pytest.fixture
def person(db_session):
    from app.models.person import Person
    p = Person(first_name="Test", last_name="Person")
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def person2(db_session):
    from app.models.person import Person
    p = Person(first_name="Another", last_name="Member")
    db_session.add(p)
    db_session.flush()
    return p


class TestMinistryCRUD:
    def test_create_ministry(self, service):
        data = MinistryCreate(name="Choir", description="Church choir")
        ministry = service.create_ministry(data)
        assert ministry.id is not None
        assert ministry.name == "Choir"
        assert ministry.is_active is True

    def test_create_ministry_with_leader(self, service, person):
        data = MinistryCreate(name="Youth", leader_id=person.id)
        ministry = service.create_ministry(data)
        # Leader should be auto-added as member
        members = service.repo.get_members(ministry.id)
        assert len(members) == 1
        assert members[0].person_id == person.id
        assert members[0].role == "leader"

    def test_create_ministry_with_invalid_leader(self, service):
        data = MinistryCreate(name="Bad", leader_id=9999)
        with pytest.raises(MinistryValidationError, match="Person with id 9999 not found"):
            service.create_ministry(data)

    def test_get_ministry(self, service):
        created = service.create_ministry(MinistryCreate(name="Test"))
        fetched = service.get_ministry(created.id)
        assert fetched is not None
        assert fetched.name == "Test"

    def test_list_ministries(self, service):
        service.create_ministry(MinistryCreate(name="Alpha"))
        service.create_ministry(MinistryCreate(name="Beta"))
        items, total = service.list_ministries()
        assert total == 2
        assert len(items) == 2

    def test_list_ministries_search(self, service):
        service.create_ministry(MinistryCreate(name="Choir"))
        service.create_ministry(MinistryCreate(name="Youth"))
        items, total = service.list_ministries(search="cho")
        assert total == 1
        assert items[0].name == "Choir"

    def test_update_ministry(self, service):
        m = service.create_ministry(MinistryCreate(name="Old"))
        updated = service.update_ministry(m.id, MinistryUpdate(name="New"))
        assert updated is not None
        assert updated.name == "New"

    def test_delete_ministry_empty(self, service):
        m = service.create_ministry(MinistryCreate(name="Empty"))
        result = service.delete_ministry(m.id)
        assert result is True
        assert service.get_ministry(m.id) is None

    def test_delete_ministry_soft(self, service, person):
        m = service.create_ministry(MinistryCreate(name="Has Members", leader_id=person.id))
        result = service.delete_ministry(m.id)
        assert result is True
        # Should be soft-deleted (is_active=False), not hard-deleted
        fetched = service.get_ministry(m.id)
        assert fetched is not None
        assert fetched.is_active is False


class TestMinistryMembers:
    def test_add_member(self, service, person):
        m = service.create_ministry(MinistryCreate(name="Test"))
        member = service.add_member(
            MinistryMemberCreate(ministry_id=m.id, person_id=person.id)
        )
        assert member.person_id == person.id
        assert member.role == "member"

    def test_add_duplicate_member(self, service, person):
        m = service.create_ministry(MinistryCreate(name="Test"))
        service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=person.id))
        with pytest.raises(MinistryValidationError, match="already a member"):
            service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=person.id))

    def test_add_member_invalid_person(self, service):
        m = service.create_ministry(MinistryCreate(name="Test"))
        with pytest.raises(MinistryValidationError, match="Person with id 9999 not found"):
            service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=9999))

    def test_remove_member(self, service, person):
        m = service.create_ministry(MinistryCreate(name="Test"))
        service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=person.id))
        result = service.remove_member(m.id, person.id)
        assert result is True

    def test_update_member_role(self, service, person):
        m = service.create_ministry(MinistryCreate(name="Test"))
        service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=person.id))
        updated = service.update_member(
            m.id, person.id, MinistryMemberUpdate(role="coordinator")
        )
        assert updated is not None
        assert updated.role == "coordinator"

    def test_get_person_ministries(self, service, person, person2):
        m1 = service.create_ministry(MinistryCreate(name="Choir"))
        m2 = service.create_ministry(MinistryCreate(name="Youth"))
        service.add_member(MinistryMemberCreate(ministry_id=m1.id, person_id=person.id))
        service.add_member(MinistryMemberCreate(ministry_id=m2.id, person_id=person.id))
        memberships = service.get_person_ministries(person.id)
        assert len(memberships) == 2


class TestMinistryEvents:
    def test_create_event(self, service):
        m = service.create_ministry(MinistryCreate(name="Choir"))
        event = service.create_event(
            MinistryEventCreate(
                ministry_id=m.id,
                title="Choir Practice",
                event_date=date(2026, 5, 1),
            )
        )
        assert event.title == "Choir Practice"

    def test_list_events(self, service):
        m = service.create_ministry(MinistryCreate(name="Choir"))
        service.create_event(
            MinistryEventCreate(ministry_id=m.id, title="E1", event_date=date(2026, 5, 1))
        )
        service.create_event(
            MinistryEventCreate(ministry_id=m.id, title="E2", event_date=date(2026, 6, 1))
        )
        events = service.list_events(m.id)
        assert len(events) == 2

    def test_delete_event(self, service):
        m = service.create_ministry(MinistryCreate(name="Choir"))
        event = service.create_event(
            MinistryEventCreate(ministry_id=m.id, title="E1", event_date=date(2026, 5, 1))
        )
        result = service.delete_event(event.id)
        assert result is True


class TestAttendance:
    def test_record_attendance(self, service, person, person2):
        m = service.create_ministry(MinistryCreate(name="Choir"))
        service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=person.id))
        service.add_member(MinistryMemberCreate(ministry_id=m.id, person_id=person2.id))
        event = service.create_event(
            MinistryEventCreate(ministry_id=m.id, title="Practice", event_date=date(2026, 5, 1))
        )
        count = service.record_attendance(event.id, [person.id, person2.id])
        assert count == 2

    def test_record_attendance_invalid_event(self, service, person):
        with pytest.raises(MinistryValidationError, match="Event with id 9999 not found"):
            service.record_attendance(9999, [person.id])

    def test_record_attendance_invalid_person(self, service):
        m = service.create_ministry(MinistryCreate(name="Choir"))
        event = service.create_event(
            MinistryEventCreate(ministry_id=m.id, title="Practice", event_date=date(2026, 5, 1))
        )
        with pytest.raises(MinistryValidationError, match="Person with id 9999 not found"):
            service.record_attendance(event.id, [9999])
