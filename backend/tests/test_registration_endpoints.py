"""Integration tests for Registration API endpoints."""

import time

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


class TestRegistrationAttendingSince:
    """Tests for attending_since field and auto-birth record creation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Add small delay between tests to avoid rate limiting."""
        time.sleep(0.2)

    def test_registration_with_attending_since(self, client, db_session):
        """Test that attending_since is stored on the Household record."""
        payload = {
            "household_name": "Attending Test Family",
            "attendingSince": "2020-06-15",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "John",
                    "lastName": "Tester",
                    "isHeadOfHousehold": True,
                }
            ],
            "relationships": [],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.household import Household

        household = (
            db_session.query(Household)
            .filter(Household.name == "Attending Test Family")
            .first()
        )
        assert household is not None
        assert str(household.attending_since) == "2020-06-15"

    def test_registration_auto_creates_birth_record(self, client, db_session):
        """Child born after household's attending_since should get a Birth record."""
        payload = {
            "household_name": "Birth Auto Family",
            "attendingSince": "2020-01-01",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "Jane",
                    "lastName": "Mother",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "child-1",
                    "firstName": "Baby",
                    "lastName": "Mother",
                    "dateOfBirth": "2022-05-10",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-1",
                    "relationshipType": "parent",
                }
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.person import Person

        baby_persons = (
            db_session.query(Person)
            .filter(Person.first_name == "Baby", Person.last_name == "Mother")
            .all()
        )
        assert len(baby_persons) == 1

        from app.models.analytics import Birth

        birth = (
            db_session.query(Birth)
            .filter(
                Birth.baby_first_name == "Baby",
                Birth.baby_last_name == "Mother",
            )
            .first()
        )
        assert birth is not None
        assert str(birth.date_of_birth) == "2022-05-10"
        assert birth.parent1_id is not None
        assert "Auto-recorded" in birth.notes

    def test_registration_no_birth_when_child_born_before_attending(
        self, client, db_session
    ):
        """Child born before household's attending_since should NOT get a Birth record."""
        payload = {
            "household_name": "No Birth Family",
            "attendingSince": "2023-01-01",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "Mark",
                    "lastName": "Father",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "child-1",
                    "firstName": "Older",
                    "lastName": "Father",
                    "dateOfBirth": "2020-03-15",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-1",
                    "relationshipType": "parent",
                }
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        births = db_session.query(Birth).filter(Birth.baby_first_name == "Older").all()
        assert len(births) == 0

    def test_registration_no_birth_without_attending_since(self, client, db_session):
        """No birth record when household has no attending_since."""
        payload = {
            "household_name": "No Attending Family",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "NoDate",
                    "lastName": "Parent",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "child-1",
                    "firstName": "Kiddo",
                    "lastName": "Parent",
                    "dateOfBirth": "2024-01-01",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-1",
                    "relationshipType": "parent",
                }
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        births = db_session.query(Birth).filter(Birth.baby_first_name == "Kiddo").all()
        assert len(births) == 0

    def test_registration_two_parents_one_birth_record(self, client, db_session):
        """Two parents linked to one child should produce exactly one Birth record with both parent IDs."""
        payload = {
            "household_name": "Two Parent Family",
            "attendingSince": "2019-01-01",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "Dad",
                    "lastName": "TwoP",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "parent-2",
                    "firstName": "Mom",
                    "lastName": "TwoP",
                    "isHeadOfHousehold": False,
                },
                {
                    "tempId": "child-1",
                    "firstName": "Junior",
                    "lastName": "TwoP",
                    "dateOfBirth": "2023-07-01",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-1",
                    "relationshipType": "parent",
                },
                {
                    "fromTempId": "parent-2",
                    "toTempId": "child-1",
                    "relationshipType": "parent",
                },
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        births = (
            db_session.query(Birth)
            .filter(
                Birth.baby_first_name == "Junior",
                Birth.baby_last_name == "TwoP",
            )
            .all()
        )
        assert len(births) == 1
        birth = births[0]
        assert birth.parent1_id is not None
        assert birth.parent2_id is not None
        assert birth.parent1_id != birth.parent2_id

    def test_registration_multiple_children_mixed_eligibility(self, client, db_session):
        """Only children born on/after attending_since get birth records."""
        payload = {
            "household_name": "Mixed Kids Family",
            "attendingSince": "2021-06-01",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "Parent",
                    "lastName": "Mixed",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "child-old",
                    "firstName": "OlderKid",
                    "lastName": "Mixed",
                    "dateOfBirth": "2019-01-01",
                    "isHeadOfHousehold": False,
                },
                {
                    "tempId": "child-new",
                    "firstName": "NewerKid",
                    "lastName": "Mixed",
                    "dateOfBirth": "2022-03-15",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-old",
                    "relationshipType": "parent",
                },
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-new",
                    "relationshipType": "parent",
                },
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        assert (
            db_session.query(Birth).filter(Birth.baby_first_name == "OlderKid").count()
            == 0
        )
        assert (
            db_session.query(Birth).filter(Birth.baby_first_name == "NewerKid").count()
            == 1
        )


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


class TestRegistrationErrorPaths:
    """Tests for generic-exception and HTTPException error handlers in registration router.

    Covers lines 60-66 (submit_registration generic Exception),
    lines 97-99 (submit_individual_registration HTTPException re-raise),
    and lines 100-106 (submit_individual_registration generic Exception).
    """

    @pytest.fixture(autouse=True)
    def _delay(self):
        """Small delay to avoid rate limiting."""
        time.sleep(0.2)

    # ------------------------------------------------------------------
    # submit_registration — generic Exception → 500 + rollback
    # ------------------------------------------------------------------

    def test_submit_registration_generic_exception_returns_500(
        self, client, monkeypatch
    ):
        """When service.register raises RuntimeError, endpoint returns 500."""
        from app.services import registration as reg_module

        def _boom(*args, **kwargs):
            raise RuntimeError("simulated failure")

        monkeypatch.setattr(reg_module.RegistrationService, "register", _boom)

        payload = {
            "household_name": "Error Test Family",
            "members": [
                {
                    "tempId": "m1",
                    "firstName": "Alice",
                    "lastName": "Error",
                }
            ],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 500
        assert "Registration failed" in response.json()["detail"]

    def test_submit_registration_http_exception_is_reraised(self, client, monkeypatch):
        """When service.register raises HTTPException(400), it is re-raised (not 500)."""
        from fastapi import HTTPException, status

        from app.services import registration as reg_module

        def _bad_request(*args, **kwargs):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="intentional 400",
            )

        monkeypatch.setattr(reg_module.RegistrationService, "register", _bad_request)

        payload = {
            "household_name": "HTTP Error Family",
            "members": [
                {
                    "tempId": "m1",
                    "firstName": "Bob",
                    "lastName": "Http",
                }
            ],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 400
        assert "intentional 400" in response.json()["detail"]

    # ------------------------------------------------------------------
    # submit_individual_registration — HTTPException re-raise (97-99)
    # ------------------------------------------------------------------

    def test_submit_individual_http_exception_reraised(self, client, monkeypatch):
        """When register_individual raises HTTPException, it is re-raised with rollback."""
        from fastapi import HTTPException, status

        from app.services import registration as reg_module

        def _bad_request_indiv(*args, **kwargs):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="individual 422",
            )

        monkeypatch.setattr(
            reg_module.RegistrationService,
            "register_individual",
            _bad_request_indiv,
        )

        payload = {
            "firstName": "Carol",
            "lastName": "Individual",
        }
        response = client.post("/api/register/individual", json=payload)
        assert response.status_code == 422
        assert "individual 422" in response.json()["detail"]

    # ------------------------------------------------------------------
    # submit_individual_registration — generic Exception → 500 (100-106)
    # ------------------------------------------------------------------

    def test_submit_individual_generic_exception_returns_500(self, client, monkeypatch):
        """When register_individual raises RuntimeError, endpoint returns 500."""
        from app.services import registration as reg_module

        def _boom_indiv(*args, **kwargs):
            raise RuntimeError("individual simulated failure")

        monkeypatch.setattr(
            reg_module.RegistrationService,
            "register_individual",
            _boom_indiv,
        )

        payload = {
            "firstName": "Dave",
            "lastName": "IndividualError",
        }
        response = client.post("/api/register/individual", json=payload)
        assert response.status_code == 500
        assert "Registration failed" in response.json()["detail"]
