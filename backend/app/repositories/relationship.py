"""Repository protocols and implementations for FamilyRelationship entities."""

from typing import Optional, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.person import Person
from app.models.relationship import FamilyRelationship


class RelationshipRepository(Protocol):
    """Protocol for FamilyRelationship data access."""

    def create(self, relationship: FamilyRelationship) -> FamilyRelationship: ...

    def get_by_id(self, relationship_id: int) -> Optional[FamilyRelationship]: ...

    def get_relationships_for_person(
        self, person_id: int
    ) -> list[FamilyRelationship]: ...

    def get_relationship_between(
        self, person_id: int, related_person_id: int
    ) -> Optional[FamilyRelationship]: ...

    def get_relationships_with_related(
        self, person_id: int
    ) -> list[FamilyRelationship]: ...

    def add(self, obj) -> None: ...

    def delete(self, obj) -> None: ...

    def commit(self) -> None: ...

    def refresh(self, obj) -> None: ...

    def person_exists(self, person_id: int) -> bool: ...


class SqlAlchemyRelationshipRepository:
    """SQLAlchemy implementation of RelationshipRepository."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, relationship: FamilyRelationship) -> FamilyRelationship:
        self.db.add(relationship)
        self.db.commit()
        self.db.refresh(relationship)
        return relationship

    def get_by_id(self, relationship_id: int) -> Optional[FamilyRelationship]:
        return self.db.get(FamilyRelationship, relationship_id)

    def get_relationships_for_person(self, person_id: int) -> list[FamilyRelationship]:
        stmt = select(FamilyRelationship).where(
            FamilyRelationship.person_id == person_id
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_relationship_between(
        self, person_id: int, related_person_id: int
    ) -> Optional[FamilyRelationship]:
        stmt = select(FamilyRelationship).where(
            FamilyRelationship.person_id == person_id,
            FamilyRelationship.related_person_id == related_person_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_relationships_with_related(
        self, person_id: int
    ) -> list[FamilyRelationship]:
        """Get relationships with eagerly-loaded related_person for family tree."""
        stmt = (
            select(FamilyRelationship)
            .options(selectinload(FamilyRelationship.related_person))
            .where(FamilyRelationship.person_id == person_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    def add(self, obj) -> None:
        self.db.add(obj)

    def delete(self, obj) -> None:
        self.db.delete(obj)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, obj) -> None:
        self.db.refresh(obj)

    def person_exists(self, person_id: int) -> bool:
        return self.db.get(Person, person_id) is not None
