"""Integration tests for Analytics API endpoints (Births, Mass Attendance, Population)."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.analytics import Birth, MassAttendance, PopulationSnapshot


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def sample_birth(db_session) -> Birth:
    """Create a sample birth record."""
    birth = Birth(
        baby_first_name="Emma",
        baby_last_name="Johnson",
        date_of_birth=date(2024, 3, 15),
        notes="Healthy baby",
    )
    db_session.add(birth)
    db_session.commit()
    db_session.refresh(birth)
    return birth


@pytest.fixture
def sample_attendance(db_session) -> MassAttendance:
    """Create a sample mass attendance record."""
    attendance = MassAttendance(
        date=date.today() - timedelta(days=7),
        mass_time="9:00 AM",
        attendance_count=150,
        notes="Easter Sunday",
    )
    db_session.add(attendance)
    db_session.commit()
    db_session.refresh(attendance)
    return attendance


@pytest.fixture
def sample_population_snapshot(db_session) -> PopulationSnapshot:
    """Create a sample population snapshot."""
    snapshot = PopulationSnapshot(
        date=date(2024, 1, 1),
        registered_members=500,
        households=150,
    )
    db_session.add(snapshot)
    db_session.commit()
    db_session.refresh(snapshot)
    return snapshot


# ==================== Births Tests ====================


class TestCreateBirth:
    """Tests for POST /api/births endpoint."""

    def test_create_birth_minimal(self, authenticated_client):
        """Test creating a birth record with minimal data."""
        response = authenticated_client.post(
            "/api/births",
            json={
                "baby_first_name": "Emma",
                "baby_last_name": "Johnson",
                "date_of_birth": "2024-03-15",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["baby_first_name"] == "Emma"
        assert data["baby_last_name"] == "Johnson"
        assert "id" in data

    def test_create_birth_full(self, authenticated_client, sample_person):
        """Test creating a birth record with all fields."""
        response = authenticated_client.post(
            "/api/births",
            json={
                "baby_first_name": "Emma",
                "baby_last_name": "Johnson",
                "date_of_birth": "2024-03-15",
                "parent1_id": sample_person.id,
                "notes": "Healthy baby girl",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["parent1_id"] == sample_person.id
        assert data["notes"] == "Healthy baby girl"

    def test_create_birth_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/births",
            json={
                "baby_first_name": "Emma",
                "baby_last_name": "Johnson",
                "date_of_birth": "2024-03-15",
            },
        )

        assert response.status_code == 401


class TestListBirths:
    """Tests for GET /api/births endpoint."""

    def test_list_births_empty(self, authenticated_client):
        """Test listing births when none exist."""
        response = authenticated_client.get("/api/births")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_births_with_data(self, authenticated_client, sample_birth):
        """Test listing births with data."""
        response = authenticated_client.get("/api/births")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    def test_list_births_filter_by_year(self, authenticated_client, sample_birth):
        """Test filtering by year."""
        response = authenticated_client.get("/api/births?year=2024")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

        response2 = authenticated_client.get("/api/births?year=2020")
        assert response2.json()["total"] == 0

    def test_list_births_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/births")

        assert response.status_code == 401


class TestGetBirth:
    """Tests for GET /api/births/{id} endpoint."""

    def test_get_birth_exists(self, authenticated_client, sample_birth):
        """Test getting an existing birth record."""
        response = authenticated_client.get(f"/api/births/{sample_birth.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_birth.id
        assert data["baby_first_name"] == "Emma"

    def test_get_birth_not_found(self, authenticated_client):
        """Test getting a nonexistent birth record."""
        response = authenticated_client.get("/api/births/9999")

        assert response.status_code == 404

    def test_get_birth_unauthenticated(self, client, sample_birth):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/births/{sample_birth.id}")

        assert response.status_code == 401


class TestBirthStatistics:
    """Tests for GET /api/births/statistics endpoint."""

    def test_get_birth_statistics(self, authenticated_client, sample_birth):
        """Test getting birth statistics."""
        response = authenticated_client.get("/api/births/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "by_year" in data
        assert "total" in data
        assert "current_year" in data

    def test_get_birth_statistics_with_year(self, authenticated_client, sample_birth):
        """Test getting birth statistics for specific year."""
        response = authenticated_client.get("/api/births/statistics?year=2024")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 0

    def test_get_birth_statistics_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/births/statistics")

        assert response.status_code == 401


class TestUpdateBirth:
    """Tests for PUT /api/births/{id} endpoint."""

    def test_update_birth_partial(self, authenticated_client, sample_birth):
        """Test partial update of a birth record."""
        response = authenticated_client.put(
            f"/api/births/{sample_birth.id}",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes"
        assert data["baby_first_name"] == "Emma"

    def test_update_birth_not_found(self, authenticated_client):
        """Test updating a nonexistent birth record."""
        response = authenticated_client.put(
            "/api/births/9999",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 404

    def test_update_birth_unauthenticated(self, client, sample_birth):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/births/{sample_birth.id}",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 401


class TestDeleteBirth:
    """Tests for DELETE /api/births/{id} endpoint."""

    def test_delete_birth(self, authenticated_client, sample_birth):
        """Test deleting a birth record."""
        response = authenticated_client.delete(f"/api/births/{sample_birth.id}")

        assert response.status_code == 204

        get_response = authenticated_client.get(f"/api/births/{sample_birth.id}")
        assert get_response.status_code == 404

    def test_delete_birth_not_found(self, authenticated_client):
        """Test deleting a nonexistent birth record."""
        response = authenticated_client.delete("/api/births/9999")

        assert response.status_code == 404

    def test_delete_birth_unauthenticated(self, client, sample_birth):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/births/{sample_birth.id}")

        assert response.status_code == 401


# ==================== Mass Attendance Tests ====================


class TestCreateAttendance:
    """Tests for POST /api/mass-attendance endpoint."""

    def test_create_attendance_minimal(self, authenticated_client):
        """Test creating an attendance record with minimal data."""
        response = authenticated_client.post(
            "/api/mass-attendance",
            json={
                "date": "2024-03-17",
                "attendance_count": 200,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["attendance_count"] == 200
        assert "id" in data

    def test_create_attendance_full(self, authenticated_client):
        """Test creating an attendance record with all fields."""
        response = authenticated_client.post(
            "/api/mass-attendance",
            json={
                "date": "2024-03-17",
                "mass_time": "9:00 AM",
                "attendance_count": 200,
                "notes": "Easter Sunday",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["mass_time"] == "9:00 AM"
        assert data["notes"] == "Easter Sunday"

    def test_create_attendance_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/mass-attendance",
            json={
                "date": "2024-03-17",
                "attendance_count": 200,
            },
        )

        assert response.status_code == 401


class TestListAttendance:
    """Tests for GET /api/mass-attendance endpoint."""

    def test_list_attendance_empty(self, authenticated_client):
        """Test listing attendance when none exist."""
        response = authenticated_client.get("/api/mass-attendance")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_attendance_with_data(self, authenticated_client, sample_attendance):
        """Test listing attendance with data."""
        response = authenticated_client.get("/api/mass-attendance")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    def test_list_attendance_filter_by_date(
        self, authenticated_client, sample_attendance
    ):
        """Test filtering by date range."""
        today = date.today()
        start = (today - timedelta(days=14)).isoformat()
        end = today.isoformat()

        response = authenticated_client.get(
            f"/api/mass-attendance?start_date={start}&end_date={end}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    def test_list_attendance_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/mass-attendance")

        assert response.status_code == 401


class TestGetAttendance:
    """Tests for GET /api/mass-attendance/{id} endpoint."""

    def test_get_attendance_exists(self, authenticated_client, sample_attendance):
        """Test getting an existing attendance record."""
        response = authenticated_client.get(
            f"/api/mass-attendance/{sample_attendance.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_attendance.id
        assert data["attendance_count"] == 150

    def test_get_attendance_not_found(self, authenticated_client):
        """Test getting a nonexistent attendance record."""
        response = authenticated_client.get("/api/mass-attendance/9999")

        assert response.status_code == 404

    def test_get_attendance_unauthenticated(self, client, sample_attendance):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/mass-attendance/{sample_attendance.id}")

        assert response.status_code == 401


class TestAttendanceStatistics:
    """Tests for GET /api/mass-attendance/statistics endpoint."""

    def test_get_attendance_statistics(self, authenticated_client, sample_attendance):
        """Test getting attendance statistics."""
        response = authenticated_client.get("/api/mass-attendance/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "weekly_average" in data
        assert "monthly_average" in data

    def test_get_attendance_statistics_with_breakdown(
        self, authenticated_client, sample_attendance
    ):
        """Test getting attendance statistics with mass time breakdown."""
        response = authenticated_client.get(
            "/api/mass-attendance/statistics?include_breakdown=true"
        )

        assert response.status_code == 200
        data = response.json()
        assert "by_mass_time" in data

    def test_get_attendance_statistics_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/mass-attendance/statistics")

        assert response.status_code == 401


class TestUpdateAttendance:
    """Tests for PUT /api/mass-attendance/{id} endpoint."""

    def test_update_attendance_partial(self, authenticated_client, sample_attendance):
        """Test partial update of an attendance record."""
        response = authenticated_client.put(
            f"/api/mass-attendance/{sample_attendance.id}",
            json={"attendance_count": 175},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["attendance_count"] == 175
        assert data["mass_time"] == "9:00 AM"

    def test_update_attendance_not_found(self, authenticated_client):
        """Test updating a nonexistent attendance record."""
        response = authenticated_client.put(
            "/api/mass-attendance/9999",
            json={"attendance_count": 175},
        )

        assert response.status_code == 404

    def test_update_attendance_unauthenticated(self, client, sample_attendance):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/mass-attendance/{sample_attendance.id}",
            json={"attendance_count": 175},
        )

        assert response.status_code == 401


class TestDeleteAttendance:
    """Tests for DELETE /api/mass-attendance/{id} endpoint."""

    def test_delete_attendance(self, authenticated_client, sample_attendance):
        """Test deleting an attendance record."""
        response = authenticated_client.delete(
            f"/api/mass-attendance/{sample_attendance.id}"
        )

        assert response.status_code == 204

        get_response = authenticated_client.get(
            f"/api/mass-attendance/{sample_attendance.id}"
        )
        assert get_response.status_code == 404

    def test_delete_attendance_not_found(self, authenticated_client):
        """Test deleting a nonexistent attendance record."""
        response = authenticated_client.delete("/api/mass-attendance/9999")

        assert response.status_code == 404

    def test_delete_attendance_unauthenticated(self, client, sample_attendance):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/mass-attendance/{sample_attendance.id}")

        assert response.status_code == 401


# ==================== Population Tests ====================


class TestCreatePopulationSnapshot:
    """Tests for POST /api/population endpoint."""

    def test_create_snapshot_minimal(self, authenticated_client):
        """Test creating a population snapshot."""
        response = authenticated_client.post(
            "/api/population",
            json={
                "date": "2024-06-01",
                "registered_members": 520,
                "households": 160,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["registered_members"] == 520
        assert data["households"] == 160
        assert "id" in data

    def test_create_snapshot_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/population",
            json={
                "date": "2024-06-01",
                "registered_members": 520,
                "households": 160,
            },
        )

        assert response.status_code == 401


class TestListPopulationSnapshots:
    """Tests for GET /api/population endpoint."""

    def test_list_snapshots_empty(self, authenticated_client):
        """Test listing snapshots when none exist."""
        response = authenticated_client.get("/api/population")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_snapshots_with_data(
        self, authenticated_client, sample_population_snapshot
    ):
        """Test listing snapshots with data."""
        response = authenticated_client.get("/api/population")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    def test_list_snapshots_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/population")

        assert response.status_code == 401


class TestGetPopulationSnapshot:
    """Tests for GET /api/population/{id} endpoint."""

    def test_get_snapshot_exists(
        self, authenticated_client, sample_population_snapshot
    ):
        """Test getting an existing population snapshot."""
        response = authenticated_client.get(
            f"/api/population/{sample_population_snapshot.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_population_snapshot.id
        assert data["registered_members"] == 500

    def test_get_snapshot_not_found(self, authenticated_client):
        """Test getting a nonexistent population snapshot."""
        response = authenticated_client.get("/api/population/9999")

        assert response.status_code == 404

    def test_get_snapshot_unauthenticated(self, client, sample_population_snapshot):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/population/{sample_population_snapshot.id}")

        assert response.status_code == 401


class TestPopulationStatistics:
    """Tests for GET /api/population/statistics endpoint."""

    def test_get_population_statistics(
        self, authenticated_client, sample_population_snapshot
    ):
        """Test getting population statistics."""
        response = authenticated_client.get("/api/population/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert "current_members" in data
        assert "current_households" in data

    def test_get_population_statistics_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/population/statistics")

        assert response.status_code == 401


class TestUpdatePopulationSnapshot:
    """Tests for PUT /api/population/{id} endpoint."""

    def test_update_snapshot_partial(
        self, authenticated_client, sample_population_snapshot
    ):
        """Test partial update of a population snapshot."""
        response = authenticated_client.put(
            f"/api/population/{sample_population_snapshot.id}",
            json={"registered_members": 510},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["registered_members"] == 510
        assert data["households"] == 150

    def test_update_snapshot_not_found(self, authenticated_client):
        """Test updating a nonexistent population snapshot."""
        response = authenticated_client.put(
            "/api/population/9999",
            json={"registered_members": 510},
        )

        assert response.status_code == 404

    def test_update_snapshot_unauthenticated(self, client, sample_population_snapshot):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/population/{sample_population_snapshot.id}",
            json={"registered_members": 510},
        )

        assert response.status_code == 401


class TestDeletePopulationSnapshot:
    """Tests for DELETE /api/population/{id} endpoint."""

    def test_delete_snapshot(self, authenticated_client, sample_population_snapshot):
        """Test deleting a population snapshot."""
        response = authenticated_client.delete(
            f"/api/population/{sample_population_snapshot.id}"
        )

        assert response.status_code == 204

        get_response = authenticated_client.get(
            f"/api/population/{sample_population_snapshot.id}"
        )
        assert get_response.status_code == 404

    def test_delete_snapshot_not_found(self, authenticated_client):
        """Test deleting a nonexistent population snapshot."""
        response = authenticated_client.delete("/api/population/9999")

        assert response.status_code == 404

    def test_delete_snapshot_unauthenticated(self, client, sample_population_snapshot):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/population/{sample_population_snapshot.id}")

        assert response.status_code == 401
