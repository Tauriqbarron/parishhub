"""Integration tests for the cross-ministry calendar events endpoint."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import User, get_current_user
from app.database import get_db
from app.main import app
from app.models.ministry import Ministry, UserRole


@pytest.fixture
def auth_client(db_session):
    """Test client with authenticated user."""
    user = User(email="priest@parish.com", name="Father Test")

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    role = UserRole(user_email="priest@parish.com", role="priest", ministry_id=None)
    db_session.add(role)
    db_session.commit()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unauth_client(db_session):
    """Test client with no authentication."""
    def override_get_db():
        yield db_session

    def override_get_current_user():
        return None

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def _create_ministry(client, name="Test Ministry"):
    """Helper to create a ministry and return its data."""
    resp = client.post("/api/ministries", json={"name": name})
    assert resp.status_code == 201
    return resp.json()


def _create_event(client, ministry_id, title, event_date, **kwargs):
    """Helper to create a ministry event."""
    data = {"ministry_id": ministry_id, "title": title, "event_date": event_date, **kwargs}
    resp = client.post(f"/api/ministries/{ministry_id}/events", json=data)
    assert resp.status_code == 201
    return resp.json()


class TestCalendarEndpoint:
    """Tests for GET /api/events."""

    def test_list_all_events_returns_events(self, auth_client):
        """Events from multiple ministries appear in one response."""
        m1 = _create_ministry(auth_client, "Choir")
        m2 = _create_ministry(auth_client, "Youth Group")
        _create_event(auth_client, m1["id"], "Choir Practice", "2026-05-10")
        _create_event(auth_client, m2["id"], "Youth Night", "2026-05-12")

        resp = auth_client.get("/api/events")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2
        titles = [e["title"] for e in data]
        assert "Choir Practice" in titles
        assert "Youth Night" in titles

    def test_list_all_events_date_filter(self, auth_client):
        """Date range filtering returns only matching events."""
        m = _create_ministry(auth_client)
        _create_event(auth_client, m["id"], "May Event", "2026-05-15")
        _create_event(auth_client, m["id"], "June Event", "2026-06-15")

        resp = auth_client.get("/api/events?date_from=2026-05-01&date_to=2026-05-31")
        assert resp.status_code == 200
        data = resp.json()
        assert all(e["event_date"].startswith("2026-05") for e in data)
        assert not any(e["title"] == "June Event" for e in data)

    def test_list_all_events_ministry_filter(self, auth_client):
        """Ministry ID filter returns only that ministry's events."""
        m1 = _create_ministry(auth_client, "Alpha")
        m2 = _create_ministry(auth_client, "Beta")
        _create_event(auth_client, m1["id"], "Alpha Event", "2026-05-10")
        _create_event(auth_client, m2["id"], "Beta Event", "2026-05-10")

        resp = auth_client.get(f"/api/events?ministry_id={m2['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert all(e["ministry_id"] == m2["id"] for e in data)

    def test_list_all_events_excludes_cancelled(self, auth_client, db_session):
        """Cancelled events are not returned."""
        m = _create_ministry(auth_client)
        e = _create_event(auth_client, m["id"], "Cancelled Meeting", "2026-05-20")
        # Cancel the event directly in DB
        from app.models.ministry import MinistryEvent
        event = db_session.get(MinistryEvent, e["id"])
        event.is_cancelled = True
        db_session.commit()

        resp = auth_client.get("/api/events")
        data = resp.json()
        assert not any(ev["title"] == "Cancelled Meeting" for ev in data)

    def test_list_all_events_excludes_inactive_ministry(self, auth_client, db_session):
        """Events from inactive ministries are not returned."""
        m = _create_ministry(auth_client, "Inactive Ministry")
        _create_event(auth_client, m["id"], "Ghost Event", "2026-05-10")
        # Deactivate ministry
        db_session.query(Ministry).filter(Ministry.id == m["id"]).update({"is_active": False})
        db_session.commit()

        resp = auth_client.get("/api/events")
        data = resp.json()
        assert not any(e["title"] == "Ghost Event" for e in data)

    def test_list_all_events_includes_ministry_name(self, auth_client):
        """Response includes ministry_name field populated."""
        m = _create_ministry(auth_client, "Rosary Group")
        _create_event(auth_client, m["id"], "Rosary", "2026-05-10")

        resp = auth_client.get("/api/events")
        data = resp.json()
        matching = [e for e in data if e["title"] == "Rosary"]
        assert len(matching) == 1
        assert matching[0]["ministry_name"] == "Rosary Group"

    def test_list_all_events_requires_auth(self, unauth_client):
        """Unauthenticated request returns 401."""
        resp = unauth_client.get("/api/events")
        assert resp.status_code == 401

    def test_list_all_events_ordered_by_date(self, auth_client):
        """Results are sorted by event_date ascending."""
        m = _create_ministry(auth_client)
        _create_event(auth_client, m["id"], "Later", "2026-05-20")
        _create_event(auth_client, m["id"], "Earlier", "2026-05-05")
        _create_event(auth_client, m["id"], "Middle", "2026-05-10")

        resp = auth_client.get("/api/events")
        data = resp.json()
        dates = [e["event_date"] for e in data]
        assert dates == sorted(dates)
