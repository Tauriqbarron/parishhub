"""Integration tests for Death API endpoints."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.death import Death
from app.models.person import Gender, Person


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def sample_person(db_session) -> Person:
    """Create a sample person in the database."""
    person = Person(
        first_name="John",
        last_name="Smith",
        email="john.smith@test.com",
        gender=Gender.MALE,
        date_of_birth=date(1950, 6, 15),
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def second_person(db_session) -> Person:
    """Create a second sample person in the database."""
    person = Person(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@test.com",
        gender=Gender.FEMALE,
        date_of_birth=date(1960, 3, 20),
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def sample_death(db_session, sample_person) -> Death:
    """Create a sample death record in the database."""
    death = Death(
        person_id=sample_person.id,
        date_of_death=date(2020, 5, 10),
        place_of_death="Auckland Hospital",
        cause_of_death="Natural causes",
        burial_date=date(2020, 5, 15),
        burial_location="Waikumete Cemetery",
    )
    db_session.add(death)
    db_session.commit()
    db_session.refresh(death)
    return death


@pytest.fixture
def multiple_deaths(db_session) -> list[Person]:
    """Create multiple persons with death records for list/statistics tests."""
    persons = []
    death_dates = [
        date(2020, 1, 10),
        date(2020, 6, 20),
        date(2021, 3, 5),
        date(2022, 8, 15),
        date(2023, 11, 30),
    ]
    for i, dod in enumerate(death_dates):
        person = Person(
            first_name=f"Person{i}",
            last_name=f"Last{i}",
            email=f"person{i}@test.com",
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
        )
        db_session.add(person)
        db_session.flush()
        death = Death(
            person_id=person.id,
            date_of_death=dod,
        )
        db_session.add(death)
        persons.append(person)
    db_session.commit()
    for p in persons:
        db_session.refresh(p)
    return persons


class TestCreateDeath:
    """Tests for POST /api/deaths endpoint."""

    def test_create_death_success(self, authenticated_client, sample_person):
        """Test creating a death record successfully."""
        response = authenticated_client.post(
            "/api/deaths",
            json={
                "person_id": sample_person.id,
                "date_of_death": "2023-01-15",
                "place_of_death": "Wellington Hospital",
                "cause_of_death": "Heart failure",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == sample_person.id
        assert data["date_of_death"] == "2023-01-15"
        assert data["place_of_death"] == "Wellington Hospital"
        assert data["cause_of_death"] == "Heart failure"
        assert "id" in data
        assert "created_at" in data

    def test_create_death_duplicate(self, authenticated_client, sample_death):
        """Test that creating a duplicate death record returns 400."""
        response = authenticated_client.post(
            "/api/deaths",
            json={
                "person_id": sample_death.person_id,
                "date_of_death": "2023-01-15",
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_death_person_not_found(self, authenticated_client):
        """Test creating a death record for nonexistent person returns 400."""
        response = authenticated_client.post(
            "/api/deaths",
            json={
                "person_id": 99999,
                "date_of_death": "2023-01-15",
            },
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    def test_create_death_future_date(self, authenticated_client, sample_person):
        """Test that a future death date returns 400."""
        future_date = (date.today() + timedelta(days=30)).isoformat()
        response = authenticated_client.post(
            "/api/deaths",
            json={
                "person_id": sample_person.id,
                "date_of_death": future_date,
            },
        )

        assert response.status_code == 400
        assert "future" in response.json()["detail"]

    def test_create_death_unauthenticated(self, client, sample_person):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            "/api/deaths",
            json={
                "person_id": sample_person.id,
                "date_of_death": "2023-01-15",
            },
        )

        assert response.status_code == 401


class TestListDeaths:
    """Tests for GET /api/deaths endpoint."""

    def test_list_deaths_empty(self, authenticated_client):
        """Test listing deaths when none exist."""
        response = authenticated_client.get("/api/deaths")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_deaths_with_data(self, authenticated_client, sample_death):
        """Test listing deaths with data."""
        response = authenticated_client.get("/api/deaths")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["person"]["first_name"] == "John"

    def test_list_deaths_year_filter(self, authenticated_client, multiple_deaths):
        """Test filtering deaths by year."""
        response = authenticated_client.get("/api/deaths?year=2020")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["date_of_death"].startswith("2020")

    def test_list_deaths_year_filter_no_results(
        self, authenticated_client, multiple_deaths
    ):
        """Test filtering deaths by year with no matches."""
        response = authenticated_client.get("/api/deaths?year=1999")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_list_deaths_pagination(self, authenticated_client, multiple_deaths):
        """Test pagination of death list."""
        response = authenticated_client.get("/api/deaths?page=1&per_page=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 2
        assert data["pages"] == 3

    def test_list_deaths_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/deaths")

        assert response.status_code == 401


class TestGetDeathStatistics:
    """Tests for GET /api/deaths/statistics endpoint."""

    def test_get_statistics_empty(self, authenticated_client):
        """Test getting statistics with no deaths."""
        response = authenticated_client.get("/api/deaths/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["current_year_count"] == 0
        assert data["by_year"] == []

    def test_get_statistics_with_data(self, authenticated_client, multiple_deaths):
        """Test getting statistics with data."""
        response = authenticated_client.get("/api/deaths/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert isinstance(data["by_year"], list)
        assert len(data["by_year"]) > 0

    def test_get_statistics_year_filter(self, authenticated_client, multiple_deaths):
        """Test getting statistics filtered by year."""
        response = authenticated_client.get("/api/deaths/statistics?year=2020")

        assert response.status_code == 200
        data = response.json()
        # year filter returns counts for that year
        assert data["total"] == 2

    def test_get_statistics_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/deaths/statistics")

        assert response.status_code == 401


class TestGetDeath:
    """Tests for GET /api/deaths/{id} endpoint."""

    def test_get_death_exists(self, authenticated_client, sample_death):
        """Test getting an existing death record."""
        response = authenticated_client.get(f"/api/deaths/{sample_death.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_death.id
        assert data["person_id"] == sample_death.person_id
        assert data["date_of_death"] == "2020-05-10"
        assert data["place_of_death"] == "Auckland Hospital"
        assert data["person"]["first_name"] == "John"
        assert data["person"]["last_name"] == "Smith"

    def test_get_death_not_found(self, authenticated_client):
        """Test getting a nonexistent death record."""
        response = authenticated_client.get("/api/deaths/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Death record not found"

    def test_get_death_unauthenticated(self, client, sample_death):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/deaths/{sample_death.id}")

        assert response.status_code == 401


class TestUpdateDeath:
    """Tests for PUT /api/deaths/{id} endpoint."""

    def test_update_death_success(self, authenticated_client, sample_death):
        """Test updating a death record successfully."""
        response = authenticated_client.put(
            f"/api/deaths/{sample_death.id}",
            json={
                "place_of_death": "Christchurch Hospital",
                "cause_of_death": "Cancer",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["place_of_death"] == "Christchurch Hospital"
        assert data["cause_of_death"] == "Cancer"
        # Unchanged fields remain
        assert data["date_of_death"] == "2020-05-10"

    def test_update_death_not_found(self, authenticated_client):
        """Test updating a nonexistent death record."""
        response = authenticated_client.put(
            "/api/deaths/99999",
            json={"place_of_death": "Nowhere"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Death record not found"

    def test_update_death_future_date(self, authenticated_client, sample_death):
        """Test that updating to a future death date returns 400."""
        future_date = (date.today() + timedelta(days=30)).isoformat()
        response = authenticated_client.put(
            f"/api/deaths/{sample_death.id}",
            json={"date_of_death": future_date},
        )

        assert response.status_code == 400
        assert "future" in response.json()["detail"]

    def test_update_death_unauthenticated(self, client, sample_death):
        """Test that unauthenticated requests return 401."""
        response = client.put(
            f"/api/deaths/{sample_death.id}",
            json={"place_of_death": "Somewhere"},
        )

        assert response.status_code == 401


class TestDeleteDeath:
    """Tests for DELETE /api/deaths/{id} endpoint."""

    def test_delete_death_success(self, authenticated_client, sample_death):
        """Test deleting a death record."""
        response = authenticated_client.delete(f"/api/deaths/{sample_death.id}")

        assert response.status_code == 204

        # Verify death is deleted
        get_response = authenticated_client.get(f"/api/deaths/{sample_death.id}")
        assert get_response.status_code == 404

    def test_delete_death_not_found(self, authenticated_client):
        """Test deleting a nonexistent death record."""
        response = authenticated_client.delete("/api/deaths/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Death record not found"

    def test_delete_death_unauthenticated(self, client, sample_death):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/deaths/{sample_death.id}")

        assert response.status_code == 401


class TestRecordPersonDeath:
    """Tests for POST /api/persons/{id}/death endpoint."""

    def test_record_person_death_success(self, authenticated_client, sample_person):
        """Test recording a death for a person."""
        response = authenticated_client.post(
            f"/api/persons/{sample_person.id}/death",
            json={
                "person_id": sample_person.id,
                "date_of_death": "2023-06-15",
                "burial_date": "2023-06-20",
                "burial_location": "Hamilton Cemetery",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == sample_person.id
        assert data["date_of_death"] == "2023-06-15"
        assert data["burial_location"] == "Hamilton Cemetery"

    def test_record_person_death_id_mismatch(
        self, authenticated_client, sample_person, second_person
    ):
        """Test that person_id mismatch between URL and body returns 400."""
        response = authenticated_client.post(
            f"/api/persons/{sample_person.id}/death",
            json={
                "person_id": second_person.id,
                "date_of_death": "2023-06-15",
            },
        )

        assert response.status_code == 400
        assert "does not match" in response.json()["detail"]

    def test_record_person_death_validation_error(
        self, authenticated_client, sample_death
    ):
        """Test that duplicate death record returns 400 via person endpoint."""
        response = authenticated_client.post(
            f"/api/persons/{sample_death.person_id}/death",
            json={
                "person_id": sample_death.person_id,
                "date_of_death": "2023-06-15",
            },
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_record_person_death_unauthenticated(self, client, sample_person):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            f"/api/persons/{sample_person.id}/death",
            json={
                "person_id": sample_person.id,
                "date_of_death": "2023-06-15",
            },
        )

        assert response.status_code == 401


class TestGetPersonDeath:
    """Tests for GET /api/persons/{id}/death endpoint."""

    def test_get_person_death_exists(self, authenticated_client, sample_death):
        """Test getting death record for a person."""
        response = authenticated_client.get(
            f"/api/persons/{sample_death.person_id}/death"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["person_id"] == sample_death.person_id
        assert data["date_of_death"] == "2020-05-10"
        assert data["person"]["first_name"] == "John"

    def test_get_person_death_not_found(self, authenticated_client, sample_person):
        """Test getting death for a person who has no death record."""
        response = authenticated_client.get(f"/api/persons/{sample_person.id}/death")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_person_death_unauthenticated(self, client, sample_death):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/persons/{sample_death.person_id}/death")

        assert response.status_code == 401
