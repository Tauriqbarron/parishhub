"""Integration tests for Household API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.household import Household, HouseholdMember, HouseholdRole


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def sample_household(db_session) -> Household:
    """Create a sample household in the database."""
    household = Household(
        name="The Smith Family",
        address_line1="123 Main Street",
        city="Auckland",
        postal_code="1010",
    )
    db_session.add(household)
    db_session.commit()
    db_session.refresh(household)
    return household


@pytest.fixture
def sample_household_with_members(db_session, sample_person) -> Household:
    """Create a sample household with members."""
    household = Household(
        name="The Jones Family",
        address_line1="456 Oak Avenue",
        city="Wellington",
    )
    db_session.add(household)
    db_session.flush()

    member = HouseholdMember(
        household_id=household.id,
        person_id=sample_person.id,
        role=HouseholdRole.HEAD,
        is_primary_household=True,
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(household)
    return household


class TestCreateHousehold:
    """Tests for POST /api/households endpoint."""

    def test_create_household_minimal(self, authenticated_client):
        """Test creating a household with minimal data."""
        response = authenticated_client.post(
            "/api/households",
            json={"name": "The Smith Family"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "The Smith Family"
        assert "id" in data
        assert "created_at" in data
        assert data["members"] == []

    def test_create_household_full(self, authenticated_client):
        """Test creating a household with all fields."""
        response = authenticated_client.post(
            "/api/households",
            json={
                "name": "The Smith Family",
                "address_line1": "123 Main Street",
                "address_line2": "Apartment 4B",
                "city": "Auckland",
                "postal_code": "1010",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "The Smith Family"
        assert data["address_line1"] == "123 Main Street"
        assert data["city"] == "Auckland"

    def test_create_household_with_members(self, authenticated_client, sample_person):
        """Test creating a household with initial members."""
        response = authenticated_client.post(
            "/api/households",
            json={
                "name": "The Test Family",
                "members": [
                    {"person_id": sample_person.id, "role": "head"},
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "The Test Family"
        assert len(data["members"]) == 1
        assert data["members"][0]["person_id"] == sample_person.id
        assert data["members"][0]["role"] == "head"

    def test_create_household_invalid_role(self, authenticated_client, sample_person):
        """Test that invalid roles are rejected."""
        response = authenticated_client.post(
            "/api/households",
            json={
                "name": "The Test Family",
                "members": [
                    {"person_id": sample_person.id, "role": "invalid_role"},
                ],
            },
        )

        assert response.status_code == 400

    def test_create_household_missing_name(self, authenticated_client):
        """Test that missing name returns 422."""
        response = authenticated_client.post(
            "/api/households",
            json={},
        )

        assert response.status_code == 422

    def test_create_household_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/households",
            json={"name": "The Smith Family"},
        )

        assert response.status_code == 401


class TestListHouseholds:
    """Tests for GET /api/households endpoint."""

    def test_list_households_empty(self, authenticated_client):
        """Test listing households when none exist."""
        response = authenticated_client.get("/api/households")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_households_with_data(self, authenticated_client, sample_household):
        """Test listing households with data."""
        response = authenticated_client.get("/api/households")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["name"] == "The Smith Family"

    def test_list_households_search(self, authenticated_client, sample_household):
        """Test search functionality."""
        response = authenticated_client.get("/api/households?search=Smith")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

        response = authenticated_client.get("/api/households?search=Jones")
        data = response.json()
        assert len(data["items"]) == 0

    def test_list_households_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/households")

        assert response.status_code == 401


class TestGetHousehold:
    """Tests for GET /api/households/{id} endpoint."""

    def test_get_household_exists(self, authenticated_client, sample_household):
        """Test getting an existing household."""
        response = authenticated_client.get(f"/api/households/{sample_household.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_household.id
        assert data["name"] == sample_household.name
        assert "members" in data

    def test_get_household_with_members(
        self, authenticated_client, sample_household_with_members
    ):
        """Test getting a household with members."""
        response = authenticated_client.get(
            f"/api/households/{sample_household_with_members.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["members"]) == 1
        assert data["members"][0]["role"] == "head"

    def test_get_household_not_found(self, authenticated_client):
        """Test getting a nonexistent household."""
        response = authenticated_client.get("/api/households/9999")

        assert response.status_code == 404

    def test_get_household_unauthenticated(self, client, sample_household):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/households/{sample_household.id}")

        assert response.status_code == 401


class TestUpdateHousehold:
    """Tests for PUT /api/households/{id} endpoint."""

    def test_update_household_partial(self, authenticated_client, sample_household):
        """Test partial update of a household."""
        response = authenticated_client.put(
            f"/api/households/{sample_household.id}",
            json={"name": "The Updated Family"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "The Updated Family"
        assert data["city"] == sample_household.city

    def test_update_household_not_found(self, authenticated_client):
        """Test updating a nonexistent household."""
        response = authenticated_client.put(
            "/api/households/9999",
            json={"name": "Test"},
        )

        assert response.status_code == 404

    def test_update_household_unauthenticated(self, client, sample_household):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/households/{sample_household.id}",
            json={"name": "Test"},
        )

        assert response.status_code == 401


class TestDeleteHousehold:
    """Tests for DELETE /api/households/{id} endpoint."""

    def test_delete_household(self, authenticated_client, sample_household):
        """Test deleting a household."""
        response = authenticated_client.delete(f"/api/households/{sample_household.id}")

        assert response.status_code == 204

        # Verify household is deleted
        get_response = authenticated_client.get(
            f"/api/households/{sample_household.id}"
        )
        assert get_response.status_code == 404

    def test_delete_household_not_found(self, authenticated_client):
        """Test deleting a nonexistent household."""
        response = authenticated_client.delete("/api/households/9999")

        assert response.status_code == 404

    def test_delete_household_unauthenticated(self, client, sample_household):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/households/{sample_household.id}")

        assert response.status_code == 401


class TestHouseholdMembers:
    """Tests for household member operations."""

    def test_add_member(self, authenticated_client, sample_household, sample_person):
        """Test adding a member to a household."""
        response = authenticated_client.post(
            f"/api/households/{sample_household.id}/members",
            params={
                "person_id": sample_person.id,
                "role": "head",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == sample_person.id
        assert data["role"] == "head"

    def test_add_member_invalid_household(self, authenticated_client, sample_person):
        """Test adding a member to a nonexistent household."""
        response = authenticated_client.post(
            "/api/households/9999/members",
            params={
                "person_id": sample_person.id,
                "role": "head",
            },
        )

        assert response.status_code == 400

    def test_add_member_duplicate(
        self, authenticated_client, sample_household_with_members, sample_person
    ):
        """Test adding a member that already exists."""
        response = authenticated_client.post(
            f"/api/households/{sample_household_with_members.id}/members",
            params={
                "person_id": sample_person.id,
                "role": "spouse",
            },
        )

        assert response.status_code == 400

    def test_update_member(
        self, authenticated_client, sample_household_with_members, sample_person
    ):
        """Test updating a member's role."""
        response = authenticated_client.put(
            f"/api/households/{sample_household_with_members.id}/members/{sample_person.id}",
            json={"role": "spouse"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "spouse"

    def test_update_member_not_found(self, authenticated_client, sample_household):
        """Test updating a nonexistent member."""
        response = authenticated_client.put(
            f"/api/households/{sample_household.id}/members/9999",
            json={"role": "spouse"},
        )

        assert response.status_code == 404

    def test_remove_member(
        self, authenticated_client, sample_household_with_members, sample_person
    ):
        """Test removing a member from a household."""
        response = authenticated_client.delete(
            f"/api/households/{sample_household_with_members.id}/members/{sample_person.id}"
        )

        assert response.status_code == 204

    def test_remove_member_not_found(self, authenticated_client, sample_household):
        """Test removing a nonexistent member."""
        response = authenticated_client.delete(
            f"/api/households/{sample_household.id}/members/9999"
        )

        assert response.status_code == 404
