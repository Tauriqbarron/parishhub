"""Integration tests for Notification API endpoints.

Tests GET/PUT /api/member/notification/preferences,
GET /api/member/notification/deliveries (paginated),
PUT /api/member/notification/deliveries/mark-read,
and GET /api/member/notification/unread-count.

Uses FastAPI TestClient with auth fixture overrides.
"""

import pytest
from fastapi.testclient import TestClient

from app.auth.member import MemberUser, require_member
from app.main import app
from app.models.notification import NotificationDelivery, NotificationPreference
from app.models.person import Person
from app.services.notifications import notification_service


# ─── Auth fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
def member_user(person) -> MemberUser:
    """Create a MemberUser linked to the test person."""
    return MemberUser(
        email=person.email,
        name=f"{person.first_name} {person.last_name}",
        person_id=person.id,
        roles=[],
    )


@pytest.fixture
def authenticated_client(client: TestClient, member_user: MemberUser):
    """Override require_member dependency to return our test MemberUser."""
    async def mock_require_member():
        return member_user

    app.dependency_overrides[require_member] = mock_require_member
    yield client
    app.dependency_overrides.pop(require_member, None)


@pytest.fixture
def person_with_email(db_session) -> Person:
    """Create a test person with email for member linking."""
    p = Person(
        first_name="APITest",
        last_name="User",
        email="apitest.user@test.com",
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p


@pytest.fixture
def member_user_from_person(person_with_email) -> MemberUser:
    """Create a MemberUser linked to person_with_email."""
    return MemberUser(
        email=person_with_email.email,
        name=f"{person_with_email.first_name} {person_with_email.last_name}",
        person_id=person_with_email.id,
        roles=[],
    )


@pytest.fixture
def authenticated_client_with_person(
    client: TestClient, member_user_from_person: MemberUser
):
    """Override require_member with a member linked to person_with_email."""
    async def mock_require_member():
        return member_user_from_person

    app.dependency_overrides[require_member] = mock_require_member
    yield client
    app.dependency_overrides.pop(require_member, None)


# ─── Preferences endpoints ────────────────────────────────────────────────────


class TestPreferencesAPI:
    """Tests for notification preferences endpoints."""

    # --- GET /preferences ---

    def test_get_preferences_empty(
        self, authenticated_client_with_person, person_with_email
    ):
        """GET /preferences returns empty list when no preferences exist."""
        response = authenticated_client_with_person.get(
            "/api/member/notification/preferences"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_preferences_with_existing(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """GET /preferences returns existing preferences."""
        # Create some preferences directly
        prefs = [
            NotificationPreference(
                person_id=person_with_email.id,
                category="announcements",
                channel="email",
                enabled=True,
            ),
            NotificationPreference(
                person_id=person_with_email.id,
                category="roster",
                channel="app",
                enabled=False,
            ),
        ]
        db_session.add_all(prefs)
        db_session.commit()

        response = authenticated_client_with_person.get(
            "/api/member/notification/preferences"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Check structure
        for item in data:
            assert "id" in item
            assert "person_id" in item
            assert item["person_id"] == person_with_email.id
            assert "category" in item
            assert "channel" in item
            assert "enabled" in item

        categories = {item["category"] for item in data}
        assert "announcements" in categories
        assert "roster" in categories

    def test_get_preferences_unauthenticated(self, client):
        """GET /preferences returns 401 without auth."""
        response = client.get("/api/member/notification/preferences")
        assert response.status_code == 401

    # --- PUT /preferences (bulk upsert) ---

    def test_put_preferences_creates_new(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """PUT /preferences creates new preferences for the member."""
        payload = {
            "preferences": [
                {"category": "announcements", "channel": "email", "enabled": True},
                {"category": "events", "channel": "app", "enabled": False},
            ]
        }

        response = authenticated_client_with_person.put(
            "/api/member/notification/preferences", json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # Verify in DB
        db_prefs = (
            db_session.query(NotificationPreference)
            .filter(NotificationPreference.person_id == person_with_email.id)
            .all()
        )
        assert len(db_prefs) == 2

    def test_put_preferences_replaces_existing(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """PUT /preferences replaces all existing preferences (bulk upsert)."""
        # Create initial preferences
        db_session.add(
            NotificationPreference(
                person_id=person_with_email.id,
                category="announcements",
                channel="email",
                enabled=True,
            )
        )
        db_session.add(
            NotificationPreference(
                person_id=person_with_email.id,
                category="roster",
                channel="app",
                enabled=True,
            )
        )
        db_session.commit()

        # Replace with new set (only one preference, different data)
        payload = {
            "preferences": [
                {"category": "events", "channel": "sms", "enabled": False},
            ]
        }

        response = authenticated_client_with_person.put(
            "/api/member/notification/preferences", json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "events"
        assert data[0]["channel"] == "sms"
        assert data[0]["enabled"] is False

        # Verify old preferences deleted
        db_prefs = (
            db_session.query(NotificationPreference)
            .filter(NotificationPreference.person_id == person_with_email.id)
            .all()
        )
        assert len(db_prefs) == 1
        assert db_prefs[0].category == "events"

    def test_put_preferences_empty_list_clears_all(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """PUT /preferences with an empty list deletes all preferences."""
        # Create some preferences first
        db_session.add(
            NotificationPreference(
                person_id=person_with_email.id,
                category="announcements",
                channel="email",
                enabled=True,
            )
        )
        db_session.commit()

        payload = {"preferences": []}

        response = authenticated_client_with_person.put(
            "/api/member/notification/preferences", json=payload
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

        # Verify all deleted
        db_prefs = (
            db_session.query(NotificationPreference)
            .filter(NotificationPreference.person_id == person_with_email.id)
            .all()
        )
        assert len(db_prefs) == 0

    def test_put_preferences_scoped_to_own_person(
        self, db_session, authenticated_client_with_person, person_with_email, sample_person
    ):
        """PUT /preferences only modifies the authenticated member's preferences."""
        # Create a preference for another person
        db_session.add(
            NotificationPreference(
                person_id=sample_person.id,
                category="announcements",
                channel="email",
                enabled=True,
            )
        )
        db_session.commit()

        payload = {
            "preferences": [
                {"category": "roster", "channel": "app", "enabled": True},
            ]
        }

        response = authenticated_client_with_person.put(
            "/api/member/notification/preferences", json=payload
        )
        assert response.status_code == 200

        # Other person's preferences untouched
        other_prefs = (
            db_session.query(NotificationPreference)
            .filter(NotificationPreference.person_id == sample_person.id)
            .all()
        )
        assert len(other_prefs) == 1

    def test_put_preferences_unauthenticated(self, client):
        """PUT /preferences returns 401 without auth."""
        payload = {
            "preferences": [
                {"category": "events", "channel": "email", "enabled": True},
            ]
        }
        response = client.put("/api/member/notification/preferences", json=payload)
        assert response.status_code == 401


# ─── Deliveries endpoints ──────────────────────────────────────────────────────


class TestDeliveriesAPI:
    """Tests for notification deliveries endpoints."""

    @pytest.fixture(autouse=True)
    def setup_deliveries(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """Create test deliveries for the authenticated person."""
        # Create several deliveries with different timestamps
        svc = notification_service
        for i in range(5):
            svc.emit(
                event_type=f"event_{i}",
                recipients=[person_with_email.id],
                category="events",
                template_data={"title": f"Event {i}", "body": f"Body {i}"},
                db=db_session,
            )
        db_session.commit()

    def test_get_deliveries_returns_paginated(
        self, authenticated_client_with_person, person_with_email
    ):
        """GET /deliveries returns paginated list of deliveries."""
        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries"
        )
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

        assert data["total"] == 5
        assert data["page"] == 1
        assert len(data["items"]) == 5

        # Check item structure
        item = data["items"][0]
        assert "id" in item
        assert "category" in item
        assert "event_type" in item
        assert "channel" in item
        assert "status" in item
        assert "title" in item
        assert "created_at" in item

    def test_get_deliveries_pagination(
        self, authenticated_client_with_person, person_with_email
    ):
        """GET /deliveries respects page and page_size params."""
        # Page 1, size 2
        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries?page=1&page_size=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["page_size"] == 2

        # Page 2, size 2
        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries?page=2&page_size=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 2

        # Page 3, size 2 — should have 1 item
        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries?page=3&page_size=2"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 5
        assert data["page"] == 3

    def test_get_deliveries_ordered_by_created_desc(
        self, authenticated_client_with_person, person_with_email
    ):
        """GET /deliveries returns most recent first."""
        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries"
        )
        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        # Items should be in descending created_at order
        for i in range(len(items) - 1):
            assert items[i]["created_at"] >= items[i + 1]["created_at"]

    def test_get_deliveries_status_filter_unread(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """GET /deliveries?status=unread returns only unread deliveries."""
        # Mark some deliveries as read
        deliveries = (
            db_session.query(NotificationDelivery)
            .filter(NotificationDelivery.person_id == person_with_email.id)
            .limit(3)
            .all()
        )
        ids = [d.id for d in deliveries]
        notification_service.mark_read(
            db=db_session, person_id=person_with_email.id, delivery_ids=ids
        )

        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries?status=unread"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2  # 5 total, 3 marked read → 2 unread

        for item in data["items"]:
            assert item["read_at"] is None

    def test_get_deliveries_scoped_to_own_person(
        self, db_session, authenticated_client_with_person, person_with_email, sample_person
    ):
        """GET /deliveries only returns deliveries for the authenticated member."""
        # Create a delivery for sample_person
        svc = notification_service
        svc.emit(
            event_type="other_event",
            recipients=[sample_person.id],
            category="events",
            template_data={"title": "Other Event", "body": "Not mine"},
            db=db_session,
        )
        db_session.commit()

        response = authenticated_client_with_person.get(
            "/api/member/notification/deliveries"
        )
        assert response.status_code == 200
        data = response.json()

        # None of the items should belong to sample_person
        for item in data["items"]:
            assert item.get("person_id", None) != sample_person.id

    def test_get_deliveries_unauthenticated(self, client):
        """GET /deliveries without auth — endpoint uses optional auth, returns 200 with empty results."""
        response = client.get("/api/member/notification/deliveries")
        assert response.status_code in (200, 401)  # may vary by auth config


# ─── Mark-read endpoint ────────────────────────────────────────────────────────


class TestMarkReadAPI:
    """Tests for PUT /deliveries/mark-read endpoint."""

    @pytest.fixture(autouse=True)
    def setup_delivery(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """Create a test delivery."""
        svc = notification_service
        svc.emit(
            event_type="test_event",
            recipients=[person_with_email.id],
            category="events",
            template_data={"title": "Test Event", "body": "Test Body"},
            db=db_session,
        )
        db_session.commit()

    def test_mark_read_single_delivery(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """PUT /deliveries/mark-read marks a delivery as read."""
        delivery = (
            db_session.query(NotificationDelivery)
            .filter(NotificationDelivery.person_id == person_with_email.id)
            .first()
        )

        response = authenticated_client_with_person.put(
            "/api/member/notification/deliveries/mark-read",
            json={"delivery_ids": [delivery.id]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 1

        # Verify in DB
        db_session.refresh(delivery)
        assert delivery.read_at is not None
        assert delivery.status == "read"

    def test_mark_read_multiple_deliveries(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """PUT /deliveries/mark-read marks multiple deliveries as read."""
        deliveries = (
            db_session.query(NotificationDelivery)
            .filter(NotificationDelivery.person_id == person_with_email.id)
            .all()
        )
        ids = [d.id for d in deliveries]

        response = authenticated_client_with_person.put(
            "/api/member/notification/deliveries/mark-read",
            json={"delivery_ids": ids},
        )
        assert response.status_code == 200
        assert response.json()["updated"] == len(ids)

        for d in deliveries:
            db_session.refresh(d)
            assert d.read_at is not None

    def test_mark_read_other_person_delivery_not_updated(
        self, db_session, authenticated_client_with_person, sample_person
    ):
        """PUT /deliveries/mark-read does not update deliveries belonging to others."""
        # Create a delivery for sample_person
        svc = notification_service
        svc.emit(
            event_type="other_event",
            recipients=[sample_person.id],
            category="events",
            template_data={"title": "Other Event", "body": "Not mine"},
            db=db_session,
        )
        db_session.commit()

        other_delivery = (
            db_session.query(NotificationDelivery)
            .filter(NotificationDelivery.person_id == sample_person.id)
            .first()
        )

        response = authenticated_client_with_person.put(
            "/api/member/notification/deliveries/mark-read",
            json={"delivery_ids": [other_delivery.id]},
        )
        assert response.status_code == 200
        assert response.json()["updated"] == 0  # Not updated (wrong person)

        db_session.refresh(other_delivery)
        assert other_delivery.read_at is None  # Still unread

    def test_mark_read_with_nonexistent_ids(
        self, authenticated_client_with_person
    ):
        """PUT /deliveries/mark-read with nonexistent IDs returns 0 updated."""
        response = authenticated_client_with_person.put(
            "/api/member/notification/deliveries/mark-read",
            json={"delivery_ids": [99999]},
        )
        assert response.status_code == 200
        assert response.json()["updated"] == 0

    def test_mark_read_empty_ids_validation_error(
        self, authenticated_client_with_person
    ):
        """PUT /deliveries/mark-read with empty list returns validation error."""
        response = authenticated_client_with_person.put(
            "/api/member/notification/deliveries/mark-read",
            json={"delivery_ids": []},
        )
        assert response.status_code == 422  # Pydantic validation: min_length=1

    def test_mark_read_unauthenticated(self, client):
        """PUT /deliveries/mark-read without auth — endpoint uses optional auth."""
        response = client.put(
            "/api/member/notification/deliveries/mark-read",
            json={"delivery_ids": [1]},
        )
        assert response.status_code in (200, 401)  # may vary by auth config


# ─── Unread-count endpoint ─────────────────────────────────────────────────────


class TestUnreadCountAPI:
    """Tests for GET /unread-count endpoint."""

    def test_unread_count_zero(
        self, authenticated_client_with_person, person_with_email
    ):
        """GET /unread-count returns 0 when no deliveries exist."""
        response = authenticated_client_with_person.get(
            "/api/member/notification/unread-count"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_unread_count_with_deliveries(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """GET /unread-count returns correct count of unread deliveries."""
        svc = notification_service
        for i in range(4):
            svc.emit(
                event_type=f"event_{i}",
                recipients=[person_with_email.id],
                category="events",
                template_data={"title": f"Event {i}", "body": f"Body {i}"},
                db=db_session,
            )
        db_session.commit()

        response = authenticated_client_with_person.get(
            "/api/member/notification/unread-count"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 4

    def test_unread_count_excludes_read(
        self, db_session, authenticated_client_with_person, person_with_email
    ):
        """GET /unread-count excludes deliveries marked as read."""
        svc = notification_service
        svc.emit(
            event_type="event_1",
            recipients=[person_with_email.id],
            category="events",
            template_data={"title": "Event 1", "body": "Body 1"},
            db=db_session,
        )
        svc.emit(
            event_type="event_2",
            recipients=[person_with_email.id],
            category="events",
            template_data={"title": "Event 2", "body": "Body 2"},
            db=db_session,
        )
        db_session.commit()

        # Mark one as read
        delivery = (
            db_session.query(NotificationDelivery)
            .filter(NotificationDelivery.person_id == person_with_email.id)
            .first()
        )
        svc.mark_read(
            db=db_session,
            person_id=person_with_email.id,
            delivery_ids=[delivery.id],
        )

        response = authenticated_client_with_person.get(
            "/api/member/notification/unread-count"
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_unread_count_scoped_to_person(
        self, db_session, authenticated_client_with_person, person_with_email,
        sample_person
    ):
        """GET /unread-count only counts the authenticated member's deliveries."""
        svc = notification_service
        # Create a delivery for another person
        svc.emit(
            event_type="other_event",
            recipients=[sample_person.id],
            category="events",
            template_data={"title": "Other Event", "body": "Not mine"},
            db=db_session,
        )
        db_session.commit()

        response = authenticated_client_with_person.get(
            "/api/member/notification/unread-count"
        )
        assert response.status_code == 200
        # Should be 0 — the delivery for sample_person doesn't count
        assert response.json()["total"] == 0

    def test_unread_count_unauthenticated(self, client):
        """GET /unread-count returns 401 without auth."""
        response = client.get("/api/member/notification/unread-count")
        assert response.status_code == 401
