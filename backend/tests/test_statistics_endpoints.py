"""Integration tests for Statistics API endpoints."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.household import Household
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
def dashboard_data(db_session) -> dict:
    """Create sample data for dashboard testing."""
    # Create persons
    persons = [
        Person(first_name="John", last_name="Smith", gender=Gender.MALE),
        Person(first_name="Jane", last_name="Smith", gender=Gender.FEMALE),
        Person(first_name="Bob", last_name="Jones", gender=Gender.MALE),
    ]
    for p in persons:
        db_session.add(p)
    db_session.commit()
    for p in persons:
        db_session.refresh(p)

    # Create households
    households = [
        Household(name="Smith Family"),
        Household(name="Jones Family"),
    ]
    for h in households:
        db_session.add(h)
    db_session.commit()
    for h in households:
        db_session.refresh(h)

    # Create sacraments for current year
    current_year = date.today().year
    sacraments = [
        Sacrament(
            person_id=persons[0].id,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(current_year, 3, 15),
        ),
        Sacrament(
            person_id=persons[1].id,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(current_year, 4, 20),
        ),
        Sacrament(
            person_id=persons[0].id,
            sacrament_type=SacramentType.MARRIAGE,
            date_received=date(current_year, 6, 1),
        ),
    ]
    for s in sacraments:
        db_session.add(s)
    db_session.commit()

    return {
        "persons": persons,
        "households": households,
        "sacraments": sacraments,
    }


class TestDashboardStatistics:
    """Tests for GET /api/statistics/dashboard endpoint."""

    def test_get_dashboard_empty(self, authenticated_client):
        """Test getting dashboard with no data."""
        response = authenticated_client.get("/api/statistics/dashboard")

        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "recent_activity" in data
        assert "sacrament_trends" in data
        assert data["stats"]["total_people"] == 0
        assert data["stats"]["total_households"] == 0

    def test_get_dashboard_with_data(self, authenticated_client, dashboard_data):
        """Test getting dashboard with data."""
        response = authenticated_client.get("/api/statistics/dashboard")

        assert response.status_code == 200
        data = response.json()

        # Check stats
        assert data["stats"]["total_people"] == 3
        assert data["stats"]["total_households"] == 2
        assert data["stats"]["baptisms_this_year"] == 2
        assert data["stats"]["marriages_this_year"] == 1

    def test_get_dashboard_recent_activity(self, authenticated_client, dashboard_data):
        """Test that recent activity is included."""
        response = authenticated_client.get("/api/statistics/dashboard")

        assert response.status_code == 200
        data = response.json()

        assert len(data["recent_activity"]) > 0
        # Should have person_added, sacrament_recorded, and household_created types
        activity_types = {a["type"] for a in data["recent_activity"]}
        assert "person_added" in activity_types

    def test_get_dashboard_sacrament_trends(self, authenticated_client, dashboard_data):
        """Test that sacrament trends are included."""
        response = authenticated_client.get("/api/statistics/dashboard")

        assert response.status_code == 200
        data = response.json()

        # Should have 5 years of data
        assert len(data["sacrament_trends"]) == 5

        # Check structure
        current_year_trend = next(
            (t for t in data["sacrament_trends"] if t["year"] == date.today().year),
            None,
        )
        assert current_year_trend is not None
        assert "baptism" in current_year_trend
        assert "first_communion" in current_year_trend
        assert "confirmation" in current_year_trend
        assert "marriage" in current_year_trend
        assert "holy_orders" in current_year_trend

    def test_get_dashboard_unauthenticated(self, client):
        """Test that unauthenticated requests return 401."""
        response = client.get("/api/statistics/dashboard")

        assert response.status_code == 401
