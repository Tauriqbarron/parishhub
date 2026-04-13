"""Tests for app/main.py endpoints and uncovered router paths."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.death import Death


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


# ─── app/main.py endpoint tests ─────────────────────────────────────────────


class TestHealthCheck:
    """Tests for GET /api/health endpoint (covers line 126)."""

    def test_health_check_returns_ok(self, client: TestClient):
        """Health check returns 200 with status ok."""
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}


class TestRootEndpoint:
    """Tests for GET / endpoint (covers line 132)."""

    def test_root_returns_api_info(self, client: TestClient):
        """Root endpoint returns API metadata."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Parish Database API" in data["message"]
        assert "docs" in data


class TestGetCurrentUserInfo:
    """Tests for GET /api/me endpoint (covers line 140)."""

    def test_get_current_user_authenticated(self, authenticated_client: TestClient):
        """Authenticated request returns user info."""
        response = authenticated_client.get("/api/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_get_current_user_unauthenticated(self, client: TestClient):
        """Unauthenticated request returns 401."""
        response = client.get("/api/me")

        assert response.status_code == 401


# ─── app/routers/sacraments.py uncovered paths ──────────────────────────────


class TestSacramentUpdateValidationError:
    """Tests for update_sacrament SacramentValidationError (covers line 204)."""

    def test_update_sacrament_date_violation(
        self, authenticated_client: TestClient, db_session, sample_person
    ):
        """Updating a Baptism to a date after First Communion raises 400."""
        # Create Baptism
        baptism_resp = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "baptism",
                "date_received": "2020-01-01",
            },
        )
        assert baptism_resp.status_code == 201
        baptism_id = baptism_resp.json()["id"]

        # Create First Communion (must be after Baptism)
        communion_resp = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "first_communion",
                "date_received": "2021-06-01",
            },
        )
        assert communion_resp.status_code == 201

        # Try to update Baptism date to AFTER First Communion
        response = authenticated_client.put(
            f"/api/sacraments/{baptism_id}",
            json={"date_received": "2022-01-01"},
        )

        assert response.status_code == 400
        assert "Baptism date must be before" in response.json()["detail"]


class TestCreatePersonSacramentValidationError:
    """Tests for create_person_sacrament SacramentValidationError (covers lines 283-284)."""

    def test_create_person_sacrament_duplicate(
        self, authenticated_client: TestClient, sample_person
    ):
        """Creating a duplicate sacrament via person-nested route raises 400."""
        # Create first Baptism via the person-nested endpoint
        resp1 = authenticated_client.post(
            f"/api/persons/{sample_person.id}/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "baptism",
                "date_received": "2020-01-01",
            },
        )
        assert resp1.status_code == 201

        # Try to create a second Baptism — should be rejected
        resp2 = authenticated_client.post(
            f"/api/persons/{sample_person.id}/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "baptism",
                "date_received": "2021-01-01",
            },
        )

        assert resp2.status_code == 400
        assert "already has a baptism" in resp2.json()["detail"]


# ─── app/routers/statistics.py uncovered paths ──────────────────────────────


class TestStatisticsDashboardWithDeaths:
    """Tests for dashboard recent_activity with deaths (covers statistics.py line 91)."""

    def test_dashboard_shows_recent_deaths(
        self, authenticated_client: TestClient, db_session, sample_person
    ):
        """Dashboard includes death records in recent activity."""
        # Create a Death record directly via the DB
        death = Death(
            person_id=sample_person.id,
            date_of_death=date(2025, 1, 15),
        )
        db_session.add(death)
        db_session.commit()

        # Hit the dashboard endpoint
        response = authenticated_client.get("/api/statistics/dashboard")

        assert response.status_code == 200
        data = response.json()
        # Verify the death appears in recent_activity
        death_activities = [
            a for a in data["recent_activity"] if a["type"] == "death_recorded"
        ]
        assert len(death_activities) >= 1


# ─── app/routers/households.py uncovered paths ──────────────────────────────


class TestCreateHouseholdMemberValidation:
    """Tests for household member validation (covers households.py line 48)."""

    def test_create_household_member_missing_role(
        self, authenticated_client: TestClient
    ):
        """Member without role raises 400."""
        response = authenticated_client.post(
            "/api/households",
            json={
                "name": "Test Household",
                "members": [{"person_id": 1}],
            },
        )

        assert response.status_code == 400
        assert "person_id and role" in response.json()["detail"]

    def test_create_household_member_missing_person_id(
        self, authenticated_client: TestClient
    ):
        """Member without person_id raises 400."""
        response = authenticated_client.post(
            "/api/households",
            json={
                "name": "Test Household",
                "members": [{"role": "head"}],
            },
        )

        assert response.status_code == 400
        assert "person_id and role" in response.json()["detail"]
