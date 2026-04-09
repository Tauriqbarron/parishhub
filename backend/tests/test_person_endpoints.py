"""Integration tests for Person API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


class TestCreatePerson:
    """Tests for POST /api/persons endpoint."""

    def test_create_person_minimal(self, authenticated_client):
        """Test creating a person with minimal data."""
        response = authenticated_client.post(
            "/api/persons",
            json={"first_name": "John", "last_name": "Smith"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Smith"
        assert "id" in data
        assert "created_at" in data

    def test_create_person_full(self, authenticated_client, full_person_data):
        """Test creating a person with all fields."""
        response = authenticated_client.post(
            "/api/persons",
            json=full_person_data,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == full_person_data["first_name"]
        assert data["middle_name"] == full_person_data["middle_name"]
        assert data["last_name"] == full_person_data["last_name"]
        assert data["email"] == full_person_data["email"]
        assert data["gender"] == full_person_data["gender"]

    def test_create_person_duplicate_email(self, authenticated_client):
        """Test that duplicate emails are rejected."""
        person_data = {
            "first_name": "John",
            "last_name": "Smith",
            "email": "duplicate@test.com",
        }

        # Create first person
        response1 = authenticated_client.post("/api/persons", json=person_data)
        assert response1.status_code == 201

        # Try to create second person with same email
        person_data["first_name"] = "Jane"
        response2 = authenticated_client.post("/api/persons", json=person_data)
        assert response2.status_code == 409

    def test_create_person_missing_required_field(self, authenticated_client):
        """Test that missing required fields return 422."""
        response = authenticated_client.post(
            "/api/persons",
            json={"first_name": "John"},  # Missing last_name
        )

        assert response.status_code == 422

    def test_create_person_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/persons",
            json={"first_name": "John", "last_name": "Smith"},
        )

        assert response.status_code == 401


class TestListPersons:
    """Tests for GET /api/persons endpoint."""

    def test_list_persons_empty(self, authenticated_client):
        """Test listing persons when none exist."""
        response = authenticated_client.get("/api/persons")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_persons_with_data(self, authenticated_client, multiple_persons):
        """Test listing persons with data."""
        response = authenticated_client.get("/api/persons")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 5

    def test_list_persons_pagination(self, authenticated_client, multiple_persons):
        """Test pagination parameters."""
        response = authenticated_client.get("/api/persons?page=1&per_page=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["pages"] == 3

    def test_list_persons_search(self, authenticated_client, multiple_persons):
        """Test search functionality."""
        response = authenticated_client.get("/api/persons?search=Alice")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["first_name"] == "Alice"

    def test_list_persons_filter_gender(self, authenticated_client, multiple_persons):
        """Test gender filtering."""
        response = authenticated_client.get("/api/persons?gender=female")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for person in data["items"]:
            assert person["gender"] == "female"

    def test_list_persons_sort_desc(self, authenticated_client, multiple_persons):
        """Test descending sort order."""
        response = authenticated_client.get(
            "/api/persons?sort_by=last_name&sort_order=desc"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["last_name"] == "Evans"

    def test_list_persons_invalid_per_page(self, authenticated_client):
        """Test that per_page over 100 returns 422."""
        response = authenticated_client.get("/api/persons?per_page=101")

        assert response.status_code == 422

    def test_list_persons_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/persons")

        assert response.status_code == 401


class TestGetPerson:
    """Tests for GET /api/persons/{id} endpoint."""

    def test_get_person_exists(self, authenticated_client, sample_person):
        """Test getting an existing person."""
        response = authenticated_client.get(f"/api/persons/{sample_person.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_person.id
        assert data["first_name"] == sample_person.first_name
        assert "household_memberships" in data
        assert "sacraments" in data

    def test_get_person_not_found(self, authenticated_client):
        """Test getting a nonexistent person."""
        response = authenticated_client.get("/api/persons/9999")

        assert response.status_code == 404

    def test_get_person_unauthenticated(self, client, sample_person):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/persons/{sample_person.id}")

        assert response.status_code == 401


class TestUpdatePerson:
    """Tests for PUT /api/persons/{id} endpoint."""

    def test_update_person_partial(self, authenticated_client, sample_person):
        """Test partial update of a person."""
        response = authenticated_client.put(
            f"/api/persons/{sample_person.id}",
            json={"first_name": "Jane"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == sample_person.last_name

    def test_update_person_full(self, authenticated_client, sample_person):
        """Test full update of a person."""
        response = authenticated_client.put(
            f"/api/persons/{sample_person.id}",
            json={
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@test.com",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Doe"
        assert data["email"] == "jane.doe@test.com"

    def test_update_person_not_found(self, authenticated_client):
        """Test updating a nonexistent person."""
        response = authenticated_client.put(
            "/api/persons/9999",
            json={"first_name": "Jane"},
        )

        assert response.status_code == 404

    def test_update_person_duplicate_email(
        self, authenticated_client, multiple_persons
    ):
        """Test that updating to a duplicate email is rejected."""
        # Try to update first person's email to second person's email
        response = authenticated_client.put(
            f"/api/persons/{multiple_persons[0].id}",
            json={"email": multiple_persons[1].email},
        )

        assert response.status_code == 409

    def test_update_person_unauthenticated(self, client, sample_person):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/persons/{sample_person.id}",
            json={"first_name": "Jane"},
        )

        assert response.status_code == 401


class TestDeletePerson:
    """Tests for DELETE /api/persons/{id} endpoint."""

    def test_delete_person(self, authenticated_client, sample_person):
        """Test deleting a person."""
        response = authenticated_client.delete(f"/api/persons/{sample_person.id}")

        assert response.status_code == 204

        # Verify person is deleted
        get_response = authenticated_client.get(f"/api/persons/{sample_person.id}")
        assert get_response.status_code == 404

    def test_delete_person_not_found(self, authenticated_client):
        """Test deleting a nonexistent person."""
        response = authenticated_client.delete("/api/persons/9999")

        assert response.status_code == 404

    def test_delete_person_unauthenticated(self, client, sample_person):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/persons/{sample_person.id}")

        assert response.status_code == 401
