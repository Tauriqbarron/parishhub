"""Tests for uncovered repository methods.

Covers: DeathRepository.create, HouseholdRepository.get_member_count/get_person,
RelationshipRepository.create/get_relationships_with_related,
PersonRepository.get_by_id_with_relations.
"""

from datetime import date


from app.models.death import Death
from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.person import Gender, Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.models.sacrament import Sacrament, SacramentType
from app.repositories.death import SqlAlchemyDeathRepository
from app.repositories.household import SqlAlchemyHouseholdRepository
from app.repositories.person import SqlAlchemyPersonRepository
from app.repositories.relationship import SqlAlchemyRelationshipRepository


# ---------------------------------------------------------------------------
# DeathRepository.create
# ---------------------------------------------------------------------------
class TestDeathRepositoryCreate:
    def test_create_returns_death_with_id(self, db_session):
        person = Person(first_name="Test", last_name="User")
        db_session.add(person)
        db_session.flush()

        repo = SqlAlchemyDeathRepository(db_session)
        death = Death(person_id=person.id, date_of_death=date(2023, 1, 15))
        result = repo.create(death)

        assert result.id is not None
        assert result.person_id == person.id
        assert result.date_of_death == date(2023, 1, 15)

    def test_create_persists_to_db(self, db_session):
        person = Person(first_name="Persist", last_name="Test")
        db_session.add(person)
        db_session.flush()

        repo = SqlAlchemyDeathRepository(db_session)
        death = Death(person_id=person.id, date_of_death=date(2022, 6, 1))
        created = repo.create(death)

        fetched = db_session.get(Death, created.id)
        assert fetched is not None
        assert fetched.date_of_death == date(2022, 6, 1)


# ---------------------------------------------------------------------------
# HouseholdRepository.get_member_count / get_person
# ---------------------------------------------------------------------------
class TestHouseholdRepositoryGetMemberCount:
    def test_empty_household_returns_zero(self, db_session):
        household = Household(name="Empty House")
        db_session.add(household)
        db_session.flush()

        repo = SqlAlchemyHouseholdRepository(db_session)
        assert repo.get_member_count(household.id) == 0

    def test_counts_members(self, db_session):
        household = Household(name="Smith Family")
        db_session.add(household)
        db_session.flush()

        p1 = Person(first_name="Alice", last_name="Smith")
        p2 = Person(first_name="Bob", last_name="Smith")
        db_session.add_all([p1, p2])
        db_session.flush()

        db_session.add_all(
            [
                HouseholdMember(
                    household_id=household.id,
                    person_id=p1.id,
                    role=HouseholdRole.HEAD,
                ),
                HouseholdMember(
                    household_id=household.id,
                    person_id=p2.id,
                    role=HouseholdRole.SPOUSE,
                ),
            ]
        )
        db_session.flush()

        repo = SqlAlchemyHouseholdRepository(db_session)
        assert repo.get_member_count(household.id) == 2


class TestHouseholdRepositoryGetPerson:
    def test_get_existing_person(self, db_session):
        person = Person(first_name="Get", last_name="Me")
        db_session.add(person)
        db_session.flush()

        repo = SqlAlchemyHouseholdRepository(db_session)
        result = repo.get_person(person.id)

        assert result is not None
        assert result.id == person.id
        assert result.first_name == "Get"

    def test_get_nonexistent_person_returns_none(self, db_session):
        repo = SqlAlchemyHouseholdRepository(db_session)
        assert repo.get_person(999999) is None


# ---------------------------------------------------------------------------
# RelationshipRepository.create / get_relationships_with_related
# ---------------------------------------------------------------------------
class TestRelationshipRepositoryCreate:
    def test_create_returns_relationship_with_id(self, db_session):
        p1 = Person(first_name="Parent", last_name="A")
        p2 = Person(first_name="Child", last_name="A")
        db_session.add_all([p1, p2])
        db_session.flush()

        repo = SqlAlchemyRelationshipRepository(db_session)
        rel = FamilyRelationship(
            person_id=p1.id,
            related_person_id=p2.id,
            relationship_type=RelationshipType.PARENT,
        )
        result = repo.create(rel)

        assert result.id is not None
        assert result.person_id == p1.id
        assert result.related_person_id == p2.id
        assert result.relationship_type == RelationshipType.PARENT


class TestRelationshipRepositoryGetRelationshipsWithRelated:
    def test_returns_relationships_with_eager_loaded_related_person(self, db_session):
        parent = Person(first_name="Parent", last_name="B")
        child = Person(first_name="Child", last_name="B")
        db_session.add_all([parent, child])
        db_session.flush()

        rel = FamilyRelationship(
            person_id=parent.id,
            related_person_id=child.id,
            relationship_type=RelationshipType.PARENT,
        )
        db_session.add(rel)
        db_session.flush()

        repo = SqlAlchemyRelationshipRepository(db_session)
        results = repo.get_relationships_with_related(parent.id)

        assert len(results) == 1
        # related_person should be eagerly loaded — accessing it should not trigger a lazy load
        related = results[0].related_person
        assert related is not None
        assert related.id == child.id
        assert related.first_name == "Child"

    def test_returns_empty_for_person_without_relationships(self, db_session):
        person = Person(first_name="Lonely", last_name="Person")
        db_session.add(person)
        db_session.flush()

        repo = SqlAlchemyRelationshipRepository(db_session)
        assert repo.get_relationships_with_related(person.id) == []


# ---------------------------------------------------------------------------
# PersonRepository.get_by_id_with_relations
# ---------------------------------------------------------------------------
class TestPersonRepositoryGetByIdWithRelations:
    def test_loads_all_relations(self, db_session):
        # Create person
        person = Person(
            first_name="Full",
            last_name="Person",
            gender=Gender.MALE,
            date_of_birth=date(1990, 5, 20),
        )
        db_session.add(person)
        db_session.flush()

        # Household membership
        household = Household(name="Test House")
        db_session.add(household)
        db_session.flush()
        db_session.add(
            HouseholdMember(
                household_id=household.id,
                person_id=person.id,
                role=HouseholdRole.HEAD,
            )
        )

        # Sacrament
        db_session.add(
            Sacrament(
                person_id=person.id,
                sacrament_type=SacramentType.BAPTISM,
                date_received=date(1990, 6, 15),
            )
        )

        # Relationship
        other = Person(first_name="Related", last_name="Person")
        db_session.add(other)
        db_session.flush()
        db_session.add(
            FamilyRelationship(
                person_id=person.id,
                related_person_id=other.id,
                relationship_type=RelationshipType.SPOUSE,
            )
        )

        # Death
        db_session.add(Death(person_id=person.id, date_of_death=date(2050, 1, 1)))

        db_session.flush()

        repo = SqlAlchemyPersonRepository(db_session)
        result = repo.get_by_id_with_relations(person.id)

        assert result is not None
        assert result.id == person.id

        # Household memberships loaded
        assert len(result.household_memberships) == 1
        assert result.household_memberships[0].household.name == "Test House"

        # Sacraments loaded
        assert len(result.sacraments) == 1
        assert result.sacraments[0].sacrament_type == SacramentType.BAPTISM

        # Relationships as person loaded
        assert len(result.relationships_as_person) == 1
        assert (
            result.relationships_as_person[0].relationship_type
            == RelationshipType.SPOUSE
        )

        # Relationships as related loaded
        assert len(result.relationships_as_related) == 0

        # Death loaded
        assert result.death is not None
        assert result.death.date_of_death == date(2050, 1, 1)

    def test_returns_none_for_nonexistent_person(self, db_session):
        repo = SqlAlchemyPersonRepository(db_session)
        assert repo.get_by_id_with_relations(999999) is None

    def test_person_without_relations_still_returns(self, db_session):
        person = Person(first_name="Bare", last_name="Person")
        db_session.add(person)
        db_session.flush()

        repo = SqlAlchemyPersonRepository(db_session)
        result = repo.get_by_id_with_relations(person.id)

        assert result is not None
        assert result.household_memberships == []
        assert result.sacraments == []
        assert result.relationships_as_person == []
        assert result.relationships_as_related == []
        assert result.death is None
