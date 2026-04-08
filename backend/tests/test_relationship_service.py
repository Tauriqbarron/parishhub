"""Unit tests for FamilyRelationshipService."""

from datetime import date

import pytest

from app.models.person import Gender, Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.schemas.relationship import FamilyRelationshipCreate
from app.services.relationship import FamilyRelationshipService


@pytest.fixture
def two_people(db_session):
    """Create two people for relationship testing."""
    alice = Person(
        first_name="Alice",
        last_name="Smith",
        gender=Gender.FEMALE,
        date_of_birth=date(1985, 1, 1),
    )
    bob = Person(
        first_name="Bob",
        last_name="Smith",
        gender=Gender.MALE,
        date_of_birth=date(1983, 5, 10),
    )
    db_session.add_all([alice, bob])
    db_session.flush()
    return alice, bob


class TestFamilyRelationshipServiceCreate:
    def test_create_relationship_with_inverse(self, db_session, two_people):
        alice, bob = two_people
        svc = FamilyRelationshipService(db_session)
        data = FamilyRelationshipCreate(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SPOUSE,
        )
        result = svc.create(data, create_inverse=True)
        assert result.person_id == alice.id
        assert result.related_person_id == bob.id
        assert result.relationship_type == RelationshipType.SPOUSE
        # Verify inverse was created
        inverse = svc.get_relationship_between(bob.id, alice.id)
        assert inverse is not None
        assert inverse.relationship_type == RelationshipType.SPOUSE

    def test_create_relationship_without_inverse(self, db_session, two_people):
        alice, bob = two_people
        svc = FamilyRelationshipService(db_session)
        data = FamilyRelationshipCreate(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.PARENT,
        )
        result = svc.create(data, create_inverse=False)
        assert result is not None
        # No inverse should exist
        inverse = svc.get_relationship_between(bob.id, alice.id)
        assert inverse is None

    def test_create_parent_child_creates_both_directions(self, db_session, two_people):
        alice, bob = two_people
        svc = FamilyRelationshipService(db_session)
        data = FamilyRelationshipCreate(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.PARENT,
        )
        svc.create(data)
        forward = svc.get_relationship_between(alice.id, bob.id)
        inverse = svc.get_relationship_between(bob.id, alice.id)
        assert forward.relationship_type == RelationshipType.PARENT
        assert inverse.relationship_type == RelationshipType.CHILD


class TestFamilyRelationshipServiceGet:
    def test_get_by_id_exists(self, db_session, two_people):
        alice, bob = two_people
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SIBLING,
        )
        db_session.add(rel)
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        result = svc.get_by_id(rel.id)
        assert result is not None
        assert result.id == rel.id

    def test_get_by_id_not_found(self, db_session):
        svc = FamilyRelationshipService(db_session)
        assert svc.get_by_id(9999) is None

    def test_get_relationships_for_person(self, db_session, two_people):
        alice, bob = two_people
        rel1 = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SIBLING,
        )
        rel2 = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.PARENT,
        )
        db_session.add_all([rel1, rel2])
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        results = svc.get_relationships_for_person(alice.id)
        assert len(results) == 2

    def test_get_relationship_between(self, db_session, two_people):
        alice, bob = two_people
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SPOUSE,
        )
        db_session.add(rel)
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        result = svc.get_relationship_between(alice.id, bob.id)
        assert result is not None
        assert result.relationship_type == RelationshipType.SPOUSE

    def test_get_relationship_between_not_found(self, db_session, two_people):
        svc = FamilyRelationshipService(db_session)
        alice, bob = two_people
        assert svc.get_relationship_between(alice.id, bob.id) is None


class TestFamilyRelationshipServiceDelete:
    def test_delete_with_inverse(self, db_session, two_people):
        alice, bob = two_people
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SPOUSE,
        )
        inverse = FamilyRelationship(
            person_id=bob.id,
            related_person_id=alice.id,
            relationship_type=RelationshipType.SPOUSE,
        )
        db_session.add_all([rel, inverse])
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        result = svc.delete(rel.id, delete_inverse=True)
        assert result is True
        assert svc.get_by_id(rel.id) is None
        assert svc.get_by_id(inverse.id) is None

    def test_delete_without_inverse(self, db_session, two_people):
        alice, bob = two_people
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.PARENT,
        )
        inverse = FamilyRelationship(
            person_id=bob.id,
            related_person_id=alice.id,
            relationship_type=RelationshipType.CHILD,
        )
        db_session.add_all([rel, inverse])
        db_session.flush()
        rel_id = rel.id
        inv_id = inverse.id
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        result = svc.delete(rel_id, delete_inverse=False)
        assert result is True
        assert svc.get_by_id(rel_id) is None
        assert svc.get_by_id(inv_id) is not None

    def test_delete_nonexistent(self, db_session):
        svc = FamilyRelationshipService(db_session)
        assert svc.delete(9999) is False


class TestFamilyRelationshipServiceFamilyTree:
    def test_empty_family_tree(self, db_session, two_people):
        alice, _ = two_people
        svc = FamilyRelationshipService(db_session)
        tree = svc.get_family_tree(alice.id)
        assert tree == {"parents": [], "children": [], "spouse": None, "siblings": []}

    def test_family_tree_with_children(self, db_session, two_people):
        alice, bob = two_people
        for p in [alice, bob]:
            p.date_of_birth = date(1990, 1, 1)
            db_session.flush()
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.CHILD,
        )
        db_session.add(rel)
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        tree = svc.get_family_tree(alice.id)
        assert len(tree["parents"]) == 1
        assert tree["parents"][0]["id"] == bob.id
        assert tree["parents"][0]["relationship_id"] == rel.id

    def test_family_tree_with_spouse(self, db_session, two_people):
        alice, bob = two_people
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SPOUSE,
        )
        db_session.add(rel)
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        tree = svc.get_family_tree(alice.id)
        assert tree["spouse"] is not None
        assert tree["spouse"]["id"] == bob.id


class TestFamilyRelationshipServiceExists:
    def test_person_exists(self, db_session, two_people):
        alice, _ = two_people
        svc = FamilyRelationshipService(db_session)
        assert svc.person_exists(alice.id) is True

    def test_person_not_exists(self, db_session):
        svc = FamilyRelationshipService(db_session)
        assert svc.person_exists(9999) is False

    def test_relationship_exists(self, db_session, two_people):
        alice, bob = two_people
        rel = FamilyRelationship(
            person_id=alice.id,
            related_person_id=bob.id,
            relationship_type=RelationshipType.SIBLING,
        )
        db_session.add(rel)
        db_session.flush()
        svc = FamilyRelationshipService(db_session)
        assert svc.relationship_exists(alice.id, bob.id) is True

    def test_relationship_not_exists(self, db_session, two_people):
        alice, bob = two_people
        svc = FamilyRelationshipService(db_session)
        assert svc.relationship_exists(alice.id, bob.id) is False


class TestFamilyTreeQueryCount:
    """Test that get_family_tree uses efficient queries (no N+1)."""

    def test_family_tree_query_count(self, db_session):
        """Verify get_family_tree executes exactly 2 queries (constant time).

        This test ensures the N+1 query problem is fixed. The get_family_tree
        method should:
        - Query all relationships for the person (1 query)
        - Eager load related Person objects via selectinload (1 query)

        Total should be exactly 2, regardless of number of family members.
        """
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        # Create a family with many relationships to test N+1 resistance
        alice = Person(first_name="Alice", last_name="Smith", email="alice@test.com")
        bob = Person(first_name="Bob", last_name="Smith", email="bob@test.com")
        carol = Person(first_name="Carol", last_name="Smith", email="carol@test.com")
        david = Person(first_name="David", last_name="Smith", email="david@test.com")
        db_session.add_all([alice, bob, carol, david])
        db_session.flush()  # assign IDs without committing

        # Create relationships: parent -> child, spouse, etc.
        relationships = [
            FamilyRelationship(
                person_id=alice.id,
                related_person_id=bob.id,
                relationship_type=RelationshipType.PARENT,
            ),
            FamilyRelationship(
                person_id=bob.id,
                related_person_id=alice.id,
                relationship_type=RelationshipType.CHILD,
            ),
            FamilyRelationship(
                person_id=alice.id,
                related_person_id=carol.id,
                relationship_type=RelationshipType.PARENT,
            ),
            FamilyRelationship(
                person_id=carol.id,
                related_person_id=alice.id,
                relationship_type=RelationshipType.CHILD,
            ),
            FamilyRelationship(
                person_id=alice.id,
                related_person_id=david.id,
                relationship_type=RelationshipType.SPOUSE,
            ),
            FamilyRelationship(
                person_id=david.id,
                related_person_id=alice.id,
                relationship_type=RelationshipType.SPOUSE,
            ),
        ]
        db_session.add_all(relationships)
        db_session.flush()  # Ensure relationship rows exist

        # Capture queries
        queries = []

        @event.listens_for(Engine, "before_cursor_execute")
        def capture_queries(conn, cursor, statement, parameters, context, executemany):
            queries.append(" ".join(statement.strip().split()))

        svc = FamilyRelationshipService(db_session)
        tree = svc.get_family_tree(alice.id)

        print(f"\nQuery count: {len(queries)}")
        for i, q in enumerate(queries, 1):
            print(f"  {i}. {q[:120]}")

        # Verify result correctness
        assert len(tree["parents"]) == 0
        assert len(tree["children"]) == 2
        assert tree["spouse"] is not None and tree["spouse"]["id"] == david.id
        assert len(tree["siblings"]) == 0

        # Expect exactly 2 SQL queries (no N+1)
        assert len(queries) == 2, (
            f"Expected 2 queries (N+1 fixed), got {len(queries)}: {queries}"
        )
        # First query should select FamilyRelationship rows for alice
        # Second query should be SELECT persons WHERE id IN (...)
