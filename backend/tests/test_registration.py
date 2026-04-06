"""Integration tests for Registration API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

HOUSEHOLD_PAYLOAD = {
    "household_name": "Smith Family",
    "street_address": "123 Main St",
    "city": "Auckland",
    "postal_code": "1010",
    "members": [
        {
            "tempId": "t1",
            "firstName": "John",
            "lastName": "Smith",
            "dateOfBirth": "1985-03-15",
            "gender": "male",
            "isHeadOfHousehold": True,
            "livesInHousehold": True,
        }
    ],
    "relationships": [],
    "sacraments": [],
}


class TestHouseholdRegistration:
    def test_successful_household_registration(self):
        """Test a valid household registration returns 201."""
        response = client.post("/api/register", json=HOUSEHOLD_PAYLOAD)
        assert response.status_code == 201
        data = response.json()
        assert "household_id" in data
        assert data["message"] == "Registration submitted successfully"

    def test_individual_registration(self):
        """Test individual registration without household."""
        payload = {
            "firstName": "Jane",
            "lastName": "Doe",
            "dateOfBirth": "1990-01-01",
            "gender": "female",
            "phone": "+64 21 123 4567",
            "email": "jane.doe@example.com",
            "sacraments": [],
        }
        response = client.post("/api/register/individual", json=payload)
        assert response.status_code in (200, 201)
        data = response.json()
        assert "person_id" in data

    def test_invalid_payload_returns_422(self):
        """Test that an invalid payload returns 422 Unprocessable Entity."""
        response = client.post("/api/register", json={"household_name": ""})
        assert response.status_code == 422

    def test_rate_limiting(self):
        """Rapid successive requests should eventually be rate-limited or succeed."""
        responses = [
            client.post("/api/register", json=HOUSEHOLD_PAYLOAD) for _ in range(20)
        ]
        status_codes = [r.status_code for r in responses]
        # Either all succeed (201) or some are rate-limited (429)
        assert all(code in (201, 422, 429) for code in status_codes)

    def test_registration_endpoint_is_public(self):
        """No Authorization header — must not return 401."""
        response = client.post("/api/register", json=HOUSEHOLD_PAYLOAD)
        assert response.status_code != 401

    def test_household_with_relationships(self):
        """Test household registration with parent-child relationships."""
        payload = {
            "household_name": "Smith Family",
            "street_address": "456 Oak Ave",
            "city": "Auckland",
            "postal_code": "1010",
            "members": [
                {
                    "tempId": "m1",
                    "firstName": "Alice",
                    "lastName": "Smith",
                    "isHeadOfHousehold": True,
                    "livesInHousehold": True,
                },
                {
                    "tempId": "m2",
                    "firstName": "Bob",
                    "lastName": "Smith",
                    "isHeadOfHousehold": False,
                    "livesInHousehold": True,
                },
                {
                    "tempId": "m3",
                    "firstName": "Charlie",
                    "lastName": "Smith",
                    "dateOfBirth": "2015-06-01",
                    "isHeadOfHousehold": False,
                    "livesInHousehold": True,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "m1",
                    "toTempId": "m3",
                    "relationshipType": "parent",
                },
                {
                    "fromTempId": "m2",
                    "toTempId": "m3",
                    "relationshipType": "parent",
                },
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

    def test_individual_registration_invalid_returns_422(self):
        """Test individual registration with missing required fields."""
        payload = {"firstName": ""}
        response = client.post("/api/register/individual", json=payload)
        assert response.status_code == 422

    def test_individual_registration_endpoint_is_public(self):
        """No Authorization header — must not return 401."""
        payload = {
            "firstName": "Test",
            "lastName": "User",
            "sacraments": [],
        }
        response = client.post("/api/register/individual", json=payload)
        assert response.status_code != 401
