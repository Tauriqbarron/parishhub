"""Service layer for FamilyRelationship operations."""

from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.relationship import FamilyRelationship, RelationshipType
from app.repositories.relationship import (
    RelationshipRepository,
    SqlAlchemyRelationshipRepository,
)
from app.schemas.relationship import FamilyRelationshipCreate


class FamilyRelationshipService:
    """Service class for FamilyRelationship CRUD operations."""

    # Mapping of inverse relationship types
    INVERSE_RELATIONSHIPS = {
        RelationshipType.PARENT: RelationshipType.CHILD,
        RelationshipType.CHILD: RelationshipType.PARENT,
        RelationshipType.SPOUSE: RelationshipType.SPOUSE,
        RelationshipType.SIBLING: RelationshipType.SIBLING,
    }

    def __init__(self, repo: RelationshipRepository) -> None:
        self.repo = repo

    def create(
        self, relationship_data: FamilyRelationshipCreate, create_inverse: bool = True
    ) -> FamilyRelationship:
        """
        Create a new family relationship.

        Args:
            relationship_data: The relationship data
            create_inverse: If True, also creates the inverse relationship
                           (e.g., if A is parent of B, B is child of A)

        Returns:
            The created relationship
        """
        relationship = FamilyRelationship(**relationship_data.model_dump())
        self.repo.add(relationship)

        # Create the inverse relationship
        if create_inverse:
            inverse_type = self.INVERSE_RELATIONSHIPS[
                relationship_data.relationship_type
            ]
            inverse = FamilyRelationship(
                person_id=relationship_data.related_person_id,
                related_person_id=relationship_data.person_id,
                relationship_type=inverse_type,
            )
            self.repo.add(inverse)

        self.repo.commit()
        self.repo.refresh(relationship)
        return relationship

    def get_by_id(self, relationship_id: int) -> Optional[FamilyRelationship]:
        """Get a relationship by ID."""
        return self.repo.get_by_id(relationship_id)

    def get_relationships_for_person(self, person_id: int) -> list[FamilyRelationship]:
        """Get all relationships for a person (both directions)."""
        return self.repo.get_relationships_for_person(person_id)

    def get_relationship_between(
        self, person_id: int, related_person_id: int
    ) -> Optional[FamilyRelationship]:
        """Get relationship from person_id to related_person_id."""
        return self.repo.get_relationship_between(person_id, related_person_id)

    def delete(self, relationship_id: int, delete_inverse: bool = True) -> bool:
        """
        Delete a relationship.

        Args:
            relationship_id: The ID of the relationship to delete
            delete_inverse: If True, also deletes the inverse relationship

        Returns:
            True if deleted, False if not found
        """
        relationship = self.repo.get_by_id(relationship_id)
        if not relationship:
            return False

        # Find and delete the inverse relationship
        if delete_inverse:
            inverse = self.repo.get_relationship_between(
                relationship.related_person_id, relationship.person_id
            )
            if inverse:
                self.repo.delete(inverse)

        self.repo.delete(relationship)
        self.repo.commit()
        return True

    def get_family_tree(self, person_id: int) -> dict:
        """
        Get full family tree for a person.

        Returns a structured dict with:
        - parents: list of parent persons
        - children: list of child persons
        - spouse: spouse person (if any)
        - siblings: list of sibling persons
        """
        relationships = self.repo.get_relationships_with_related(person_id)

        family_tree: dict = {
            "parents": [],
            "children": [],
            "spouse": None,
            "siblings": [],
        }

        for rel in relationships:
            related_person = rel.related_person
            if not related_person:
                continue

            person_data = {
                "id": related_person.id,
                "first_name": related_person.first_name,
                "middle_name": related_person.middle_name,
                "last_name": related_person.last_name,
                "relationship_id": rel.id,
            }

            if rel.relationship_type == RelationshipType.PARENT:
                family_tree["children"].append(person_data)
            elif rel.relationship_type == RelationshipType.CHILD:
                family_tree["parents"].append(person_data)
            elif rel.relationship_type == RelationshipType.SPOUSE:
                family_tree["spouse"] = person_data
            elif rel.relationship_type == RelationshipType.SIBLING:
                family_tree["siblings"].append(person_data)

        return family_tree

    def person_exists(self, person_id: int) -> bool:
        """Check if a person exists."""
        return self.repo.person_exists(person_id)

    def relationship_exists(self, person_id: int, related_person_id: int) -> bool:
        """Check if a relationship already exists between two people."""
        return self.get_relationship_between(person_id, related_person_id) is not None


def get_relationship_service(
    db: Session = Depends(get_db),
) -> FamilyRelationshipService:
    """Dependency to get FamilyRelationshipService instance."""
    return FamilyRelationshipService(SqlAlchemyRelationshipRepository(db))
