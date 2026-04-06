"""Integration tests for Sacrament API endpoints."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.person import Gender, Person
from app.models.sacrament import Sacrament, SacramentType


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def person_with_baptism(db_session) -> tuple[Person, Sacrament]:
    """Create a person with a baptism record."""
    person = Person(
        first_name="John",
        last_name="Smith",
        gender=Gender.MALE,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)

    sacrament = Sacrament(
        person_id=person.id,
        sacrament_type=SacramentType.BAPTISM,
        date_received=date(2010, 5, 15),
        notes="Baptized at St. Mary's",
    )
    db_session.add(sacrament)
    db_session.commit()
    db_session.refresh(sacrament)
    return person, sacrament


class TestCreateSacrament:
    """Tests for POST /api/sacraments endpoint."""

    def test_create_sacrament_minimal(self, authenticated_client, sample_person):
        """Test creating a sacrament with minimal data."""
        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "baptism",
                "date_received": "2020-01-15",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == sample_person.id
        assert data["sacrament_type"] == "baptism"
        assert data["date_received"] == "2020-01-15"
        assert "id" in data
        assert "created_at" in data

    def test_create_sacrament_full(self, authenticated_client, sample_person):
        """Test creating a sacrament with all fields."""
        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "baptism",
                "date_received": "2020-01-15",
                "notes": "Baptized with family",
                "godfather": "James Smith",
                "godmother": "Jane Doe",
            },
        )

        data = response.json()
        assert data["notes"] == "Baptized with family"
        assert data["godfather"] == "James Smith"
        assert data["godmother"] == "Jane Doe"

    def test_create_sacrament_person_not_found(self, authenticated_client):
        """Test creating sacrament for nonexistent person."""
        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": 9999,
                "sacrament_type": "baptism",
                "date_received": "2020-01-15",
            },
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_create_sacrament_duplicate(
        self, authenticated_client, person_with_baptism
    ):
        """Test that duplicate sacrament types are rejected (except marriage)."""
        person, _ = person_with_baptism
        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "baptism",
                "date_received": "2021-01-15",
            },
        )

        assert response.status_code == 400
        assert "already has" in response.json()["detail"].lower()

    def test_create_sacrament_invalid_order(
        self, authenticated_client, person_with_baptism
    ):
        """Test that first communion before baptism is rejected."""
        person, baptism = person_with_baptism
        # Try to create first communion before baptism date
        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "first_communion",
                "date_received": "2009-01-01",  # Before baptism in 2010
            },
        )

        assert response.status_code == 400
        assert "after baptism" in response.json()["detail"].lower()

    def test_create_sacrament_unauthenticated(self, client, sample_person):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/sacraments",
            json={
                "person_id": sample_person.id,
                "sacrament_type": "baptism",
                "date_received": "2020-01-15",
            },
        )

        assert response.status_code == 401


class TestListSacraments:
    """Tests for GET /api/sacraments endpoint."""

    def test_list_sacraments_empty(self, authenticated_client):
        """Test listing sacraments when none exist."""
        response = authenticated_client.get("/api/sacraments")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_sacraments_with_data(self, authenticated_client, person_with_baptism):
        """Test listing sacraments with data."""
        response = authenticated_client.get("/api/sacraments")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1

    def test_list_sacraments_filter_by_type(
        self, authenticated_client, person_with_baptism
    ):
        """Test filtering by sacrament type."""
        response = authenticated_client.get("/api/sacraments?sacrament_type=baptism")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

        response2 = authenticated_client.get(
            "/api/sacraments?sacrament_type=confirmation"
        )
        assert response2.json()["items"] == []

    def test_list_sacraments_filter_by_date(
        self, authenticated_client, person_with_baptism
    ):
        """Test filtering by date range."""
        response = authenticated_client.get(
            "/api/sacraments?date_from=2010-01-01&date_to=2010-12-31"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    def test_list_sacraments_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/sacraments")

        assert response.status_code == 401


class TestGetSacrament:
    """Tests for GET /api/sacraments/{id} endpoint."""

    def test_get_sacrament_exists(self, authenticated_client, person_with_baptism):
        """Test getting an existing sacrament."""
        _, sacrament = person_with_baptism
        response = authenticated_client.get(f"/api/sacraments/{sacrament.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sacrament.id
        assert data["sacrament_type"] == "baptism"

    def test_get_sacrament_not_found(self, authenticated_client):
        """Test getting a nonexistent sacrament."""
        response = authenticated_client.get("/api/sacraments/9999")

        assert response.status_code == 404

    def test_get_sacrament_unauthenticated(self, client, person_with_baptism):
        """Test that unauthenticated requests return 401."""
        _, sacrament = person_with_baptism
        response = client.get(f"/api/sacraments/{sacrament.id}")

        assert response.status_code == 401


class TestGetSacramentStatistics:
    """Tests for GET /api/sacraments/statistics endpoint."""

    def test_get_statistics(self, authenticated_client, person_with_baptism):
        """Test getting sacrament statistics."""
        response = authenticated_client.get("/api/sacraments/statistics")

        assert response.status_code == 200
        data = response.json()
        assert "total_baptisms" in data
        assert "by_year" in data

    def test_get_statistics_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/sacraments/statistics")

        assert response.status_code == 401


class TestUpdateSacrament:
    """Tests for PUT /api/sacraments/{id} endpoint."""

    def test_update_sacrament_partial(self, authenticated_client, person_with_baptism):
        """Test partial update of a sacrament."""
        _, sacrament = person_with_baptism
        response = authenticated_client.put(
            f"/api/sacraments/{sacrament.id}",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes"
        assert data["date_received"] == "2010-05-15"

    def test_update_sacrament_not_found(self, authenticated_client):
        """Test updating a nonexistent sacrament."""
        response = authenticated_client.put(
            "/api/sacraments/9999",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 404

    def test_update_sacrament_unauthenticated(self, client, person_with_baptism):
        """Test that unauthenticated requests return 401."""
        _, sacrament = person_with_baptism
        response = client.put(
            f"/api/sacraments/{sacrament.id}",
            json={"notes": "Updated notes"},
        )

        assert response.status_code == 401


class TestDeleteSacrament:
    """Tests for DELETE /api/sacraments/{id} endpoint."""

    def test_delete_sacrament(self, authenticated_client, person_with_baptism):
        """Test deleting a sacrament."""
        _, sacrament = person_with_baptism
        response = authenticated_client.delete(f"/api/sacraments/{sacrament.id}")

        assert response.status_code == 204

        # Verify sacrament is deleted
        get_response = authenticated_client.get(f"/api/sacraments/{sacrament.id}")
        assert get_response.status_code == 404

    def test_delete_sacrament_not_found(self, authenticated_client):
        """Test deleting a nonexistent sacrament."""
        response = authenticated_client.delete("/api/sacraments/9999")

        assert response.status_code == 404

    def test_delete_sacrament_unauthenticated(self, client, person_with_baptism):
        """Test that unauthenticated requests return 401."""
        _, sacrament = person_with_baptism
        response = client.delete(f"/api/sacraments/{sacrament.id}")

        assert response.status_code == 401


class TestPersonSacramentEndpoints:
    """Tests for person-nested sacrament endpoints."""

    def test_create_person_sacrament(self, authenticated_client, sample_person):
        """Test creating a sacrament via person endpoint."""
        response = authenticated_client.post(
            f"/api/persons/{sample_person.id}/sacraments",
            json={
                "person_id": 0,  # Will be overridden
                "sacrament_type": "baptism",
                "date_received": "2020-01-15",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == sample_person.id

    def test_get_person_sacraments(self, authenticated_client, person_with_baptism):
        """Test getting all sacraments for a person."""
        person, _ = person_with_baptism
        response = authenticated_client.get(f"/api/persons/{person.id}/sacraments")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sacrament_type"] == "baptism"

    def test_get_person_sacraments_unauthenticated(self, client, person_with_baptism):
        """Test that unauthenticated requests return 401."""
        person, _ = person_with_baptism
        response = client.get(f"/api/persons/{person.id}/sacraments")

        assert response.status_code == 401
