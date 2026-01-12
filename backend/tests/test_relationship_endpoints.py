"""Integration tests for FamilyRelationship API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.auth import User, require_auth
from app.main import app
from app.models.person import Gender, Person
from app.models.relationship import FamilyRelationship, RelationshipType


@pytest.fixture
def authenticated_client(client: TestClient):
    """Create a test client with mocked authentication."""

    async def mock_require_auth():
        return User(email="test@example.com", name="Test User")

    app.dependency_overrides[require_auth] = mock_require_auth
    yield client
    app.dependency_overrides.pop(require_auth, None)


@pytest.fixture
def parent_person(db_session) -> Person:
    """Create a parent person in the database."""
    person = Person(
        first_name="John",
        last_name="Smith",
        email="john.parent@test.com",
        gender=Gender.MALE,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def child_person(db_session) -> Person:
    """Create a child person in the database."""
    person = Person(
        first_name="Jane",
        last_name="Smith",
        email="jane.child@test.com",
        gender=Gender.FEMALE,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def spouse_person(db_session) -> Person:
    """Create a spouse person in the database."""
    person = Person(
        first_name="Mary",
        last_name="Smith",
        email="mary.spouse@test.com",
        gender=Gender.FEMALE,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def existing_relationship(db_session, parent_person, child_person) -> FamilyRelationship:
    """Create an existing parent-child relationship."""
    # Parent -> child relationship
    relationship = FamilyRelationship(
        person_id=parent_person.id,
        related_person_id=child_person.id,
        relationship_type=RelationshipType.PARENT,
    )
    db_session.add(relationship)

    # Child -> parent relationship (inverse)
    inverse = FamilyRelationship(
        person_id=child_person.id,
        related_person_id=parent_person.id,
        relationship_type=RelationshipType.CHILD,
    )
    db_session.add(inverse)

    db_session.commit()
    db_session.refresh(relationship)
    return relationship


class TestCreateRelationship:
    """Tests for POST /api/persons/{id}/relationships endpoint."""

    def test_create_parent_child_relationship(
        self, authenticated_client, parent_person, child_person
    ):
        """Test creating a parent-child relationship."""
        response = authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": child_person.id,
                "relationship_type": "parent",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["person_id"] == parent_person.id
        assert data["related_person_id"] == child_person.id
        assert data["relationship_type"] == "parent"

    def test_create_spouse_relationship(
        self, authenticated_client, parent_person, spouse_person
    ):
        """Test creating a spouse relationship."""
        response = authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": spouse_person.id,
                "relationship_type": "spouse",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["relationship_type"] == "spouse"

    def test_create_sibling_relationship(
        self, authenticated_client, child_person, spouse_person
    ):
        """Test creating a sibling relationship."""
        response = authenticated_client.post(
            f"/api/persons/{child_person.id}/relationships",
            json={
                "related_person_id": spouse_person.id,
                "relationship_type": "sibling",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["relationship_type"] == "sibling"

    def test_create_relationship_person_not_found(self, authenticated_client, child_person):
        """Test creating relationship with nonexistent person."""
        response = authenticated_client.post(
            "/api/persons/9999/relationships",
            json={
                "related_person_id": child_person.id,
                "relationship_type": "parent",
            },
        )

        assert response.status_code == 404

    def test_create_relationship_related_person_not_found(
        self, authenticated_client, parent_person
    ):
        """Test creating relationship with nonexistent related person."""
        response = authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": 9999,
                "relationship_type": "parent",
            },
        )

        assert response.status_code == 404

    def test_create_relationship_with_self(self, authenticated_client, parent_person):
        """Test that creating relationship with self is rejected."""
        response = authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": parent_person.id,
                "relationship_type": "parent",
            },
        )

        assert response.status_code == 400

    def test_create_duplicate_relationship(
        self, authenticated_client, existing_relationship, parent_person, child_person
    ):
        """Test that duplicate relationships are rejected."""
        response = authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": child_person.id,
                "relationship_type": "sibling",
            },
        )

        assert response.status_code == 409

    def test_create_relationship_unauthenticated(self, client, parent_person, child_person):
        """Test that unauthenticated requests return 401."""
        response = client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": child_person.id,
                "relationship_type": "parent",
            },
        )

        assert response.status_code == 401


class TestGetRelationships:
    """Tests for GET /api/persons/{id}/relationships endpoint."""

    def test_get_relationships_empty(self, authenticated_client, parent_person):
        """Test getting relationships when none exist."""
        response = authenticated_client.get(
            f"/api/persons/{parent_person.id}/relationships"
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_relationships_with_data(
        self, authenticated_client, existing_relationship, parent_person
    ):
        """Test getting relationships with data."""
        response = authenticated_client.get(
            f"/api/persons/{parent_person.id}/relationships"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["relationship_type"] == "parent"

    def test_get_relationships_person_not_found(self, authenticated_client):
        """Test getting relationships for nonexistent person."""
        response = authenticated_client.get("/api/persons/9999/relationships")

        assert response.status_code == 404

    def test_get_relationships_unauthenticated(self, client, parent_person):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/persons/{parent_person.id}/relationships")

        assert response.status_code == 401


class TestGetFamilyTree:
    """Tests for GET /api/persons/{id}/family-tree endpoint."""

    def test_get_family_tree_empty(self, authenticated_client, parent_person):
        """Test getting family tree when no relationships exist."""
        response = authenticated_client.get(
            f"/api/persons/{parent_person.id}/family-tree"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["parents"] == []
        assert data["children"] == []
        assert data["spouse"] is None
        assert data["siblings"] == []

    def test_get_family_tree_with_child(
        self, authenticated_client, existing_relationship, parent_person, child_person
    ):
        """Test getting family tree with parent-child relationship."""
        # Get parent's family tree - should show child
        response = authenticated_client.get(
            f"/api/persons/{parent_person.id}/family-tree"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["children"]) == 1
        assert data["children"][0]["id"] == child_person.id

        # Get child's family tree - should show parent
        response = authenticated_client.get(
            f"/api/persons/{child_person.id}/family-tree"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["parents"]) == 1
        assert data["parents"][0]["id"] == parent_person.id

    def test_get_family_tree_person_not_found(self, authenticated_client):
        """Test getting family tree for nonexistent person."""
        response = authenticated_client.get("/api/persons/9999/family-tree")

        assert response.status_code == 404

    def test_get_family_tree_unauthenticated(self, client, parent_person):
        """Test that unauthenticated requests return 401."""
        response = client.get(f"/api/persons/{parent_person.id}/family-tree")

        assert response.status_code == 401


class TestDeleteRelationship:
    """Tests for DELETE /api/relationships/{id} endpoint."""

    def test_delete_relationship(
        self, authenticated_client, existing_relationship, parent_person
    ):
        """Test deleting a relationship."""
        response = authenticated_client.delete(
            f"/api/relationships/{existing_relationship.id}"
        )

        assert response.status_code == 204

        # Verify relationship is deleted
        get_response = authenticated_client.get(
            f"/api/persons/{parent_person.id}/relationships"
        )
        assert get_response.status_code == 200
        assert get_response.json() == []

    def test_delete_relationship_removes_inverse(
        self, authenticated_client, existing_relationship, child_person
    ):
        """Test that deleting relationship also removes inverse."""
        authenticated_client.delete(f"/api/relationships/{existing_relationship.id}")

        # Check that the inverse relationship (child -> parent) is also gone
        get_response = authenticated_client.get(
            f"/api/persons/{child_person.id}/relationships"
        )
        assert get_response.status_code == 200
        assert get_response.json() == []

    def test_delete_relationship_not_found(self, authenticated_client):
        """Test deleting a nonexistent relationship."""
        response = authenticated_client.delete("/api/relationships/9999")

        assert response.status_code == 404

    def test_delete_relationship_unauthenticated(self, client, existing_relationship):
        """Test that unauthenticated requests return 401."""
        response = client.delete(f"/api/relationships/{existing_relationship.id}")

        assert response.status_code == 401


class TestBidirectionalRelationships:
    """Tests for bidirectional relationship logic."""

    def test_parent_child_creates_inverse(
        self, authenticated_client, parent_person, child_person
    ):
        """Test that creating parent relationship creates child inverse."""
        # Create parent -> child relationship
        authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": child_person.id,
                "relationship_type": "parent",
            },
        )

        # Check that child has parent relationship back
        response = authenticated_client.get(
            f"/api/persons/{child_person.id}/relationships"
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["relationship_type"] == "child"
        assert data[0]["related_person_id"] == parent_person.id

    def test_spouse_creates_symmetric(
        self, authenticated_client, parent_person, spouse_person
    ):
        """Test that spouse relationship creates symmetric inverse."""
        # Create spouse relationship
        authenticated_client.post(
            f"/api/persons/{parent_person.id}/relationships",
            json={
                "related_person_id": spouse_person.id,
                "relationship_type": "spouse",
            },
        )

        # Check that spouse also has spouse relationship
        response = authenticated_client.get(
            f"/api/persons/{spouse_person.id}/relationships"
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["relationship_type"] == "spouse"
        assert data[0]["related_person_id"] == parent_person.id

    def test_sibling_creates_symmetric(
        self, authenticated_client, child_person, spouse_person
    ):
        """Test that sibling relationship creates symmetric inverse."""
        # Create sibling relationship
        authenticated_client.post(
            f"/api/persons/{child_person.id}/relationships",
            json={
                "related_person_id": spouse_person.id,
                "relationship_type": "sibling",
            },
        )

        # Check that other person also has sibling relationship
        response = authenticated_client.get(
            f"/api/persons/{spouse_person.id}/relationships"
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["relationship_type"] == "sibling"
        assert data[0]["related_person_id"] == child_person.id
