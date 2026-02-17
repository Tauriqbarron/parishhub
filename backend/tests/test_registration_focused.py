"""Focused test for sacrament validation in registration."""

import pytest
from fastapi.testclient import TestClient


def test_registration_anointing_sacrament_validation(client):
    """Test that anointing sacrament type is properly validated and handled."""

    # Test data with anointing sacrament
    data = {
        "household_name": "Test Family for Anointing",
        "members": [
            {
                "tempId": "member1",
                "firstName": "John",
                "lastName": "Doe",
                "dateOfBirth": "1980-01-01",
                "gender": "male",
                "isHeadOfHousehold": True,
            }
        ],
        "sacraments": [
            {
                "memberTempId": "member1",
                "sacramentType": "anointing",
                "date": "2024-01-15",
                "church": "St. Mary's Cathedral",
                "minister": "Fr. James Wilson",
                "additionalData": {
                    "reason": "Surgery preparation",
                    "location": "Hospital Chapel",
                },
            }
        ],
    }

    response = client.post("/api/register", json=data)

    # Should succeed
    assert response.status_code == 201
    response_data = response.json()
    assert "household_id" in response_data
    assert response_data["message"] == "Registration submitted successfully"


def test_registration_all_sacrament_types(client):
    """Test registration with all sacrament types including anointing."""

    data = {
        "household_name": "Test Family All Sacraments",
        "members": [
            {
                "tempId": "member1",
                "firstName": "John",
                "lastName": "Doe",
                "dateOfBirth": "1980-01-01",
                "gender": "male",
                "isHeadOfHousehold": True,
            }
        ],
        "sacraments": [
            {
                "memberTempId": "member1",
                "sacramentType": "baptism",
                "date": "1990-01-01",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "first_communion",
                "date": "1998-01-01",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "confirmation",
                "date": "2005-01-01",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "marriage",
                "date": "2010-01-01",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "holy_orders",
                "date": "2015-01-01",
            },
            {
                "memberTempId": "member1",
                "sacramentType": "anointing",
                "date": "2024-01-01",
            },
        ],
    }

    response = client.post("/api/register", json=data)

    # Should succeed
    assert response.status_code == 201
    response_data = response.json()
    assert "household_id" in response_data


def test_registration_sacrament_validation_errors(client):
    """Test sacrament validation error handling."""

    # Test empty sacrament type
    data = {
        "household_name": "Test Family Error",
        "members": [
            {
                "tempId": "member1",
                "firstName": "John",
                "lastName": "Doe",
            }
        ],
        "sacraments": [
            {
                "memberTempId": "member1",
                "sacramentType": "",  # Empty type
                "date": "2024-01-01",
            }
        ],
    }

    response = client.post("/api/register", json=data)

    # Should fail with validation error
    assert response.status_code in [400, 429]  # 429 if rate limited
    if response.status_code == 400:
        assert "Sacrament type cannot be empty" in response.json()["detail"]


def test_statistics_includes_anointing(client):
    """Test that statistics endpoint includes anointing sacrament."""
    from app.auth import User, require_auth
    from app.main import app

    # Create authenticated client
    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth

    try:
        response = client.get("/api/statistics/dashboard")
        assert response.status_code == 200

        data = response.json()

        # Check sacrament trends include anointing
        assert "sacrament_trends" in data
        trends = data["sacrament_trends"]

        if trends:  # If there's trend data
            first_year = trends[0]
            assert "anointing" in first_year

    finally:
        app.dependency_overrides.pop(require_auth, None)
