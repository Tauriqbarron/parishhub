"""Integration tests for Ministries API endpoints."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import User, get_current_user
from app.database import get_db
from app.main import app
from app.models.ministry import UserRole
from app.models.person import Person


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

    # Add global priest role
    role = UserRole(user_email="priest@parish.com", role="priest", ministry_id=None)
    db_session.add(role)
    db_session.commit()

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def member_client(db_session):
    """Test client authenticated as a regular member."""
    user = User(email="member@parish.com", name="Member Test")

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    role = UserRole(user_email="member@parish.com", role="member", ministry_id=None)
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


@pytest.fixture
def sample_person(db_session):
    p = Person(first_name="John", last_name="Doe")
    db_session.add(p)
    db_session.flush()
    return p


class TestMinistryEndpoints:
    def test_create_ministry(self, auth_client):
        resp = auth_client.post("/api/ministries", json={"name": "Choir"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Choir"
        assert data["is_active"] is True

    def test_create_ministry_unauth(self, unauth_client):
        resp = unauth_client.post("/api/ministries", json={"name": "Choir"})
        assert resp.status_code == 401

    def test_member_can_create_ministry(self, member_client):
        """Authenticated members can create ministries (ParishHub: all auth users = admins)."""
        resp = member_client.post("/api/ministries", json={"name": "Choir"})
        assert resp.status_code == 201

    def test_list_ministries(self, auth_client):
        auth_client.post("/api/ministries", json={"name": "Choir"})
        auth_client.post("/api/ministries", json={"name": "Youth"})
        resp = auth_client.get("/api/ministries")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2

    def test_get_ministry_detail(self, auth_client):
        create = auth_client.post("/api/ministries", json={"name": "Choir"}).json()
        resp = auth_client.get(f"/api/ministries/{create['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Choir"

    def test_update_ministry(self, auth_client):
        create = auth_client.post("/api/ministries", json={"name": "Old"}).json()
        resp = auth_client.put(f"/api/ministries/{create['id']}", json={"name": "New"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "New"

    def test_delete_ministry(self, auth_client):
        create = auth_client.post("/api/ministries", json={"name": "Delete Me"}).json()
        resp = auth_client.delete(f"/api/ministries/{create['id']}")
        assert resp.status_code == 204


class TestMemberEndpoints:
    def test_add_member(self, auth_client, sample_person):
        m = auth_client.post("/api/ministries", json={"name": "Choir"}).json()
        resp = auth_client.post(
            f"/api/ministries/{m['id']}/members",
            json={"ministry_id": m["id"], "person_id": sample_person.id},
        )
        assert resp.status_code == 201

    def test_remove_member(self, auth_client, sample_person):
        m = auth_client.post("/api/ministries", json={"name": "Choir"}).json()
        auth_client.post(
            f"/api/ministries/{m['id']}/members",
            json={"ministry_id": m["id"], "person_id": sample_person.id},
        )
        resp = auth_client.delete(f"/api/ministries/{m['id']}/members/{sample_person.id}")
        assert resp.status_code == 204


class TestEventEndpoints:
    def test_create_event(self, auth_client):
        m = auth_client.post("/api/ministries", json={"name": "Choir"}).json()
        resp = auth_client.post(
            f"/api/ministries/{m['id']}/events",
            json={
                "ministry_id": m["id"],
                "title": "Practice",
                "event_date": "2026-05-01",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "Practice"

    def test_list_events(self, auth_client):
        m = auth_client.post("/api/ministries", json={"name": "Choir"}).json()
        auth_client.post(
            f"/api/ministries/{m['id']}/events",
            json={"ministry_id": m["id"], "title": "E1", "event_date": "2026-05-01"},
        )
        resp = auth_client.get(f"/api/ministries/{m['id']}/events")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestAttendanceEndpoints:
    def test_record_attendance(self, auth_client, sample_person):
        m = auth_client.post("/api/ministries", json={"name": "Choir"}).json()
        auth_client.post(
            f"/api/ministries/{m['id']}/members",
            json={"ministry_id": m["id"], "person_id": sample_person.id},
        )
        event = auth_client.post(
            f"/api/ministries/{m['id']}/events",
            json={"ministry_id": m["id"], "title": "Practice", "event_date": "2026-05-01"},
        ).json()
        resp = auth_client.post(
            f"/api/ministries/{m['id']}/events/{event['id']}/attendance",
            json={"person_ids": [sample_person.id]},
        )
        assert resp.status_code == 200
        assert resp.json()["recorded"] == 1


class TestRBAC:
    def test_member_can_create_ministry(self, member_client):
        """Authenticated members can create ministries (ParishHub: all auth users = admins)."""
        resp = member_client.post("/api/ministries", json={"name": "Nope"})
        assert resp.status_code == 201

    def test_member_can_get_statistics(self, member_client):
        """Authenticated members can access statistics (ParishHub: all auth users = admins)."""
        resp = member_client.get("/api/ministries/statistics")
        assert resp.status_code == 200

    def test_unauth_returns_401(self, unauth_client):
        resp = unauth_client.get("/api/ministries")
        assert resp.status_code == 401
