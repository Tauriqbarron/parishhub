"""Integration tests for Mass Times API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.mass_times import MassTime
from datetime import time


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def sample_mass_time(db_session) -> MassTime:
    """Create a sample mass time record."""
    mass_time = MassTime(
        name="Sunday Morning Mass",
        time=time(9, 0),
        day_of_week=0,
        is_active=True,
    )
    db_session.add(mass_time)
    db_session.commit()
    db_session.refresh(mass_time)
    return mass_time


@pytest.fixture
def multiple_mass_times(db_session) -> list[MassTime]:
    """Create multiple mass time records."""
    mass_times = [
        MassTime(
            name="Early Morning Mass", time=time(7, 0), day_of_week=0, is_active=True
        ),
        MassTime(name="Morning Mass", time=time(9, 0), day_of_week=0, is_active=True),
        MassTime(name="Noon Mass", time=time(12, 0), day_of_week=0, is_active=True),
        MassTime(name="Evening Mass", time=time(18, 0), day_of_week=0, is_active=False),
    ]
    for mt in mass_times:
        db_session.add(mt)
    db_session.commit()
    for mt in mass_times:
        db_session.refresh(mt)
    return mass_times


class TestCreateMassTime:
    """Tests for POST /api/mass-times endpoint."""

    def test_create_mass_time_minimal(self, authenticated_client):
        """Test creating a mass time with minimal data."""
        response = authenticated_client.post(
            "/api/mass-times",
            json={
                "name": "Sunday Mass",
                "time": "09:00:00",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sunday Mass"
        assert data["time"] == "09:00:00"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_mass_time_full(self, authenticated_client):
        """Test creating a mass time with all fields."""
        response = authenticated_client.post(
            "/api/mass-times",
            json={
                "name": "Sunday Morning Mass",
                "time": "09:00:00",
                "day_of_week": 0,
                "is_active": True,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Sunday Morning Mass"
        assert data["day_of_week"] == 0

    def test_create_mass_time_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/mass-times",
            json={
                "name": "Sunday Mass",
                "time": "09:00:00",
            },
        )

        assert response.status_code == 401


class TestListMassTimes:
    """Tests for GET /api/mass-times endpoint."""

    def test_list_mass_times_empty(self, authenticated_client):
        """Test listing mass times when none exist."""
        response = authenticated_client.get("/api/mass-times")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_mass_times_with_data(self, authenticated_client, sample_mass_time):
        """Test listing mass times with data."""
        response = authenticated_client.get("/api/mass-times")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Sunday Morning Mass"

    def test_list_mass_times_active_only(
        self, authenticated_client, multiple_mass_times
    ):
        """Test listing only active mass times (default)."""
        response = authenticated_client.get("/api/mass-times")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3  # 3 active, 1 inactive

    def test_list_mass_times_include_inactive(
        self, authenticated_client, multiple_mass_times
    ):
        """Test listing all mass times including inactive."""
        response = authenticated_client.get("/api/mass-times?active_only=false")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_list_mass_times_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/mass-times")

        assert response.status_code == 401


class TestGetMassTime:
    """Tests for GET /api/mass-times/{id} endpoint."""

    def test_get_mass_time_exists(self, authenticated_client, sample_mass_time):
        """Test getting an existing mass time."""
        response = authenticated_client.get(f"/api/mass-times/{sample_mass_time.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_mass_time.id
        assert data["name"] == "Sunday Morning Mass"

    def test_get_mass_time_not_found(self, authenticated_client):
        """Test getting a nonexistent mass time."""
        response = authenticated_client.get("/api/mass-times/9999")

        assert response.status_code == 404

    def test_get_mass_time_unauthenticated(self, client, sample_mass_time):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/mass-times/{sample_mass_time.id}")

        assert response.status_code == 401


class TestUpdateMassTime:
    """Tests for PUT /api/mass-times/{id} endpoint."""

    def test_update_mass_time_partial(self, authenticated_client, sample_mass_time):
        """Test partial update of a mass time."""
        response = authenticated_client.put(
            f"/api/mass-times/{sample_mass_time.id}",
            json={"name": "Updated Mass Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Mass Name"
        assert data["time"] == "09:00:00"

    def test_update_mass_time_deactivate(self, authenticated_client, sample_mass_time):
        """Test deactivating a mass time."""
        response = authenticated_client.put(
            f"/api/mass-times/{sample_mass_time.id}",
            json={"is_active": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        assert data["name"] == "Sunday Morning Mass"

    def test_update_mass_time_not_found(self, authenticated_client):
        """Test updating a nonexistent mass time."""
        response = authenticated_client.put(
            "/api/mass-times/9999",
            json={"name": "Updated"},
        )

        assert response.status_code == 404

    def test_update_mass_time_unauthenticated(self, client, sample_mass_time):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/mass-times/{sample_mass_time.id}",
            json={"name": "Updated"},
        )

        assert response.status_code == 401


class TestDeleteMassTime:
    """Tests for DELETE /api/mass-times/{id} endpoint."""

    def test_delete_mass_time(self, authenticated_client, sample_mass_time):
        """Test deleting (deactivating) a mass time."""
        response = authenticated_client.delete(f"/api/mass-times/{sample_mass_time.id}")

        assert response.status_code == 204

        # Verify mass time is now inactive (soft delete)
        get_response = authenticated_client.get(
            f"/api/mass-times/{sample_mass_time.id}"
        )
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] is False

    def test_delete_mass_time_not_found(self, authenticated_client):
        """Test deleting a nonexistent mass time."""
        response = authenticated_client.delete("/api/mass-times/9999")

        assert response.status_code == 404

    def test_delete_mass_time_unauthenticated(self, client, sample_mass_time):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/mass-times/{sample_mass_time.id}")

        assert response.status_code == 401
