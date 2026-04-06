"""Integration tests for marriage sacrament household auto-creation and undo."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.auth import User, require_auth
from app.main import app
from app.models.household import Household, HouseholdMember, HouseholdRole
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


def _create_person(db_session, first_name, last_name, gender="male"):
    """Helper to create a test person."""
    person = Person(
        first_name=first_name,
        last_name=last_name,
        gender=Gender.MALE if gender == "male" else Gender.FEMALE,
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


def _create_household_with_child(db_session, name, child_person):
    """Helper to create a household and add a person as CHILD."""
    household = Household(name=name)
    db_session.add(household)
    db_session.commit()
    member = HouseholdMember(
        household_id=household.id,
        person_id=child_person.id,
        role=HouseholdRole.CHILD,
        is_primary_household=True,
    )
    db_session.add(member)
    db_session.commit()
    return household


def _create_parent_relationship(db_session, parent, child):
    """Helper to create bidirectional parent-child relationship."""
    db_session.add(
        FamilyRelationship(
            person_id=parent.id,
            related_person_id=child.id,
            relationship_type=RelationshipType.PARENT,
        )
    )
    db_session.add(
        FamilyRelationship(
            person_id=child.id,
            related_person_id=parent.id,
            relationship_type=RelationshipType.CHILD,
        )
    )
    db_session.commit()


class TestMarriageHouseholdCreation:
    """Tests for auto-creating household when marriage is recorded."""

    def test_marriage_creates_household(self, authenticated_client, db_session):
        """Recording marriage with spouse_id creates a new household."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")

        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["marriage_side_effects"]["household_created"] is True
        assert data["marriage_side_effects"]["household_id"] is not None

        household = db_session.get(
            Household, data["marriage_side_effects"]["household_id"]
        )
        assert household is not None
        assert household.origin_sacrament_id == data["id"]

    def test_marriage_creates_spouse_relationship(
        self, authenticated_client, db_session
    ):
        """Recording marriage creates bidirectional SPOUSE FamilyRelationship."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Doe", "female")

        authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )

        fwd = db_session.execute(
            select(FamilyRelationship).where(
                FamilyRelationship.person_id == person.id,
                FamilyRelationship.related_person_id == spouse.id,
                FamilyRelationship.relationship_type == RelationshipType.SPOUSE,
            )
        ).scalar_one_or_none()
        assert fwd is not None

        inv = db_session.execute(
            select(FamilyRelationship).where(
                FamilyRelationship.person_id == spouse.id,
                FamilyRelationship.related_person_id == person.id,
                FamilyRelationship.relationship_type == RelationshipType.SPOUSE,
            )
        ).scalar_one_or_none()
        assert inv is not None

    def test_marriage_same_last_name_household_name(
        self, authenticated_client, db_session
    ):
        """Household named 'The Smith Family' when both have same last name."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")

        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )
        assert (
            response.json()["marriage_side_effects"]["household_name"]
            == "The Smith Family"
        )

    def test_marriage_different_last_name_household_name(
        self, authenticated_client, db_session
    ):
        """Household named 'Smith & Jones Family' when different last names."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Jones", "female")

        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )
        assert (
            response.json()["marriage_side_effects"]["household_name"]
            == "Smith & Jones Family"
        )

    def test_marriage_removes_child_from_parent_household(
        self, authenticated_client, db_session
    ):
        """Person is removed from parent household where role=CHILD."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")
        parent_household = _create_household_with_child(
            db_session, "The Smith Family", person
        )

        authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )

        child_membership = db_session.execute(
            select(HouseholdMember).where(
                HouseholdMember.person_id == person.id,
                HouseholdMember.household_id == parent_household.id,
            )
        ).scalar_one_or_none()
        assert child_membership is None

    def test_marriage_preserves_parent_relationship(
        self, authenticated_client, db_session
    ):
        """FamilyRelationship PARENT/CHILD is NOT affected by marriage."""
        parent = _create_person(db_session, "Robert", "Smith")
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")
        _create_parent_relationship(db_session, parent, person)
        _create_household_with_child(db_session, "The Smith Family", person)

        authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )

        parent_rel = db_session.execute(
            select(FamilyRelationship).where(
                FamilyRelationship.person_id == parent.id,
                FamilyRelationship.related_person_id == person.id,
                FamilyRelationship.relationship_type == RelationshipType.PARENT,
            )
        ).scalar_one_or_none()
        assert parent_rel is not None

    def test_marriage_no_spouse_id_defers_household(
        self, authenticated_client, db_session
    ):
        """No household created when spouse_id is null; household_deferred=true."""
        person = _create_person(db_session, "John", "Smith")

        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {},
            },
        )
        data = response.json()
        assert data["marriage_side_effects"]["household_created"] is False
        assert data["additional_data"]["household_deferred"] is True

    def test_marriage_both_spouses_children(self, authenticated_client, db_session):
        """Both spouses removed from their parent households."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Jones", "female")
        smith_hh = _create_household_with_child(db_session, "The Smith Family", person)
        jones_hh = _create_household_with_child(db_session, "The Jones Family", spouse)

        authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )

        assert (
            db_session.execute(
                select(HouseholdMember).where(
                    HouseholdMember.person_id == person.id,
                    HouseholdMember.household_id == smith_hh.id,
                )
            ).scalar_one_or_none()
            is None
        )

        assert (
            db_session.execute(
                select(HouseholdMember).where(
                    HouseholdMember.person_id == spouse.id,
                    HouseholdMember.household_id == jones_hh.id,
                )
            ).scalar_one_or_none()
            is None
        )

    def test_remarriage_creates_second_household(
        self, authenticated_client, db_session
    ):
        """Second marriage creates another household without error."""
        person = _create_person(db_session, "John", "Smith")
        spouse1 = _create_person(db_session, "Jane", "Smith", "female")
        spouse2 = _create_person(db_session, "Mary", "Brown", "female")

        r1 = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2020-06-15",
                "additional_data": {"spouse_id": spouse1.id},
            },
        )
        r2 = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse2.id},
            },
        )
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert (
            r1.json()["marriage_side_effects"]["household_id"]
            != r2.json()["marriage_side_effects"]["household_id"]
        )

    def test_marriage_existing_spouse_relationship_not_duplicated(
        self, authenticated_client, db_session
    ):
        """If SPOUSE relationship already exists, don't create duplicate."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")
        db_session.add(
            FamilyRelationship(
                person_id=person.id,
                related_person_id=spouse.id,
                relationship_type=RelationshipType.SPOUSE,
            )
        )
        db_session.add(
            FamilyRelationship(
                person_id=spouse.id,
                related_person_id=person.id,
                relationship_type=RelationshipType.SPOUSE,
            )
        )
        db_session.commit()

        response = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )
        data = response.json()
        assert data["marriage_side_effects"]["spouse_relationship_created"] is False
        assert data["marriage_side_effects"]["household_created"] is True


class TestUndoMarriageHousehold:
    """Tests for DELETE /api/sacraments/{id}/auto-household."""

    def test_undo_deletes_household(self, authenticated_client, db_session):
        """Undo deletes the auto-created household."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")

        create_resp = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )
        sacrament_id = create_resp.json()["id"]
        household_id = create_resp.json()["marriage_side_effects"]["household_id"]

        undo_resp = authenticated_client.delete(
            f"/api/sacraments/{sacrament_id}/auto-household"
        )
        assert undo_resp.status_code == 204

        assert db_session.get(Household, household_id) is None

    def test_undo_cascades_members(self, authenticated_client, db_session):
        """Undo removes HouseholdMember rows via cascade."""
        person = _create_person(db_session, "John", "Smith")
        spouse = _create_person(db_session, "Jane", "Smith", "female")

        create_resp = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "marriage",
                "date_received": "2025-06-15",
                "additional_data": {"spouse_id": spouse.id},
            },
        )
        sacrament_id = create_resp.json()["id"]
        household_id = create_resp.json()["marriage_side_effects"]["household_id"]

        authenticated_client.delete(f"/api/sacraments/{sacrament_id}/auto-household")

        members = (
            db_session.execute(
                select(HouseholdMember).where(
                    HouseholdMember.household_id == household_id,
                )
            )
            .scalars()
            .all()
        )
        assert len(members) == 0

    def test_undo_nonexistent_returns_404(self, authenticated_client, db_session):
        """Returns 404 if no auto-created household for this sacrament."""
        response = authenticated_client.delete("/api/sacraments/99999/auto-household")
        assert response.status_code == 404

    def test_undo_non_marriage_returns_404(self, authenticated_client, db_session):
        """Returns 404 if the sacrament is not a marriage (no auto-household)."""
        person = _create_person(db_session, "John", "Smith")

        create_resp = authenticated_client.post(
            "/api/sacraments",
            json={
                "person_id": person.id,
                "sacrament_type": "baptism",
                "date_received": "2025-06-15",
            },
        )
        sacrament_id = create_resp.json()["id"]

        response = authenticated_client.delete(
            f"/api/sacraments/{sacrament_id}/auto-household"
        )
        assert response.status_code == 404
