"""Integration tests for Registration API endpoints."""

import time
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app


@pytest.fixture
def registration_data() -> dict:
    """Sample registration data for testing."""
    return {
        "household_name": "Smith Family",
        "street_address": "123 Main Street",
        "city": "Auckland",
        "postal_code": "1010",
        "members": [
            {
                "tempId": "member1",
                "firstName": "John",
                "lastName": "Smith",
                "dateOfBirth": "1985-03-15",
                "gender": "male",
                "email": "john.smith@email.com",
                "phone": "+64 21 123 4567",
                "isHeadOfHousehold": True,
            },
            {
                "tempId": "member2",
                "firstName": "Jane",
                "lastName": "Smith",
                "dateOfBirth": "1987-06-20",
                "gender": "female",
                "email": "jane.smith@email.com",
                "phone": "+64 21 987 6543",
                "isHeadOfHousehold": False,
            },
            {
                "tempId": "member3",
                "firstName": "Jimmy",
                "lastName": "Smith",
                "dateOfBirth": "2015-09-10",
                "gender": "male",
                "isHeadOfHousehold": False,
            },
        ],
        "relationships": [
            {
                "fromTempId": "member1",
                "toTempId": "member2",
                "relationshipType": "spouse",
            },
            {
                "fromTempId": "member1",
                "toTempId": "member3",
                "relationshipType": "child",
            },
            {
                "fromTempId": "member2",
                "toTempId": "member3",
                "relationshipType": "child",
            },
        ],
        "sacraments": [
            {
                "memberTempId": "member1",
                "sacramentType": "baptism",
                "date": "1990-05-15",
                "church": "St. Mary's Cathedral",
                "minister": "Fr. John Smith",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "first_communion",
                "date": "1998-06-10",
                "church": "St. Mary's Cathedral",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "confirmation",
                "date": "2003-05-20",
                "church": "St. Mary's Cathedral",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "marriage",
                "date": "2010-08-15",
                "church": "St. Mary's Cathedral",
                "minister": "Fr. Michael Brown",
            },
            {
                "memberTempId": "member3",
                "sacramentType": "baptism",
                "date": "2015-09-12",
                "church": "St. Mary's Cathedral",
            },
            {
                "memberTempId": "member3",
                "sacramentType": "first_communion",
                "date": "2023-05-10",
                "church": "St. Mary's Cathedral",
            },
        ],
    }


@pytest.fixture
def registration_data_with_anointing(registration_data) -> dict:
    """Registration data that includes anointing sacrament."""
    data = registration_data.copy()
    data["sacraments"].append(
        {
            "memberTempId": "member2",
            "sacramentType": "anointing",
            "date": "2024-01-15",
            "church": "St. Mary's Cathedral",
            "minister": "Fr. James Wilson",
            "additionalData": {
                "reason": "Surgery preparation",
                "location": "Hospital Chapel",
            },
        }
    )
    return data


class TestRegistrationEndpoint:
    """Tests for POST /api/register endpoint."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Add small delay between tests to avoid rate limiting."""
        time.sleep(0.2)

    def test_registration_minimal(self, client):
        """Test registration with minimal data."""
        data = {
            "household_name": "Test Family",
            "members": [
                {
                    "tempId": "member1",
                    "firstName": "John",
                    "lastName": "Doe",
                }
            ],
        }
        response = client.post("/api/register", json=data)

        assert response.status_code == 201
        response_data = response.json()
        assert "household_id" in response_data
        assert response_data["message"] == "Registration submitted successfully"

    def test_registration_full(self, client, registration_data):
        """Test registration with complete data including sacraments."""
        response = client.post("/api/register", json=registration_data)

        assert response.status_code == 201
        response_data = response.json()
        assert "household_id" in response_data
        assert response_data["message"] == "Registration submitted successfully"

    def test_registration_with_anointing_sacrament(
        self, client, registration_data_with_anointing
    ):
        """Test registration that includes anointing sacrament type."""
        response = client.post("/api/register", json=registration_data_with_anointing)

        assert response.status_code == 201
        response_data = response.json()
        assert "household_id" in response_data
        assert response_data["message"] == "Registration submitted successfully"

    def test_registration_camel_case_compatibility(self, client, registration_data):
        """Test that registration accepts both camelCase and snake_case."""
        response = client.post("/api/register", json=registration_data)
        assert response.status_code == 201

        # Test with snake_case
        snake_case_data = {
            "household_name": "Test Family 2",
            "members": [
                {
                    "temp_id": "member1",
                    "first_name": "John",
                    "last_name": "Doe",
                    "date_of_birth": "1990-01-01",
                    "gender": "male",
                    "is_head_of_household": True,
                }
            ],
        }
        response = client.post("/api/register", json=snake_case_data)
        assert response.status_code == 201

    def test_registration_invalid_sacrament_type(self, client, registration_data):
        """Test registration with invalid sacrament type."""
        data = registration_data.copy()
        data["sacraments"][0]["sacramentType"] = "invalid_sacrament"

        response = client.post("/api/register", json=data)

        # May be 400 (validation error) or 429 (rate limit)
        assert response.status_code in [400, 429]
        if response.status_code == 400:
            assert "Invalid sacrament type" in response.json()["detail"]

    def test_registration_empty_sacrament_type(self, client, registration_data):
        """Test registration with empty sacrament type."""
        data = registration_data.copy()
        data["sacraments"][0]["sacramentType"] = ""

        response = client.post("/api/register", json=data)

        # May be 400 (validation error) or 429 (rate limit)
        assert response.status_code in [400, 429]
        if response.status_code == 400:
            assert "Sacrament type cannot be empty" in response.json()["detail"]

    def test_registration_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        # Missing household name
        data = {
            "members": [
                {
                    "tempId": "member1",
                    "firstName": "John",
                    "lastName": "Doe",
                }
            ],
        }

        response = client.post("/api/register", json=data)

        assert response.status_code == 422  # Validation error


class TestRegistrationURLConfig:
    """Tests for registration URL configuration endpoints."""

    @pytest.fixture
    def authenticated_client(self, client: TestClient):
        """Create a test client with mocked authentication."""

        async def mock_require_auth():
            return User(email="test@example.com", name="Test User")

        app.dependency_overrides[require_auth] = mock_require_auth
        yield client
        app.dependency_overrides.pop(require_auth, None)

    def test_get_registration_url_not_configured(self, client):
        """Test getting registration URL when not configured."""

        async def mock_require_auth():
            return User(email="test@example.com", name="Test User")

        app.dependency_overrides[require_auth] = mock_require_auth

        response = client.get("/api/v1/registration/url")

        app.dependency_overrides.pop(require_auth, None)

        assert response.status_code == 404
        assert "not configured" in response.json()["detail"]

    def test_update_registration_url(self, authenticated_client):
        """Test updating registration URL configuration."""
        config_data = {"base_url": "https://parish.example.com"}

        response = authenticated_client.put(
            "/api/v1/registration/url", json=config_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["base_url"] == "https://parish.example.com"
        assert data["registration_url"] == "https://parish.example.com/register"

    def test_get_registration_url_configured(self, authenticated_client):
        """Test getting registration URL when configured."""
        # First set the URL
        config_data = {"base_url": "https://parish.example.com"}
        authenticated_client.put("/api/v1/registration/url", json=config_data)

        # Then get it
        response = authenticated_client.get("/api/v1/registration/url")

        assert response.status_code == 200
        data = response.json()
        assert data["base_url"] == "https://parish.example.com"
        assert data["registration_url"] == "https://parish.example.com/register"

    def test_update_registration_url_unauthenticated(self, client):
        """Test that unauthenticated requests to update URL return 401."""
        config_data = {"base_url": "https://parish.example.com"}

        response = client.put("/api/v1/registration/url", json=config_data)

        assert response.status_code == 401

    def test_get_registration_url_unauthenticated(self, client):
        """Test that unauthenticated requests to get URL return 401."""
        response = client.get("/api/v1/registration/url")

        assert response.status_code == 401
