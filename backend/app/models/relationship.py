from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.person import Person


class RelationshipType(str, PyEnum):
    PARENT = "parent"
    CHILD = "child"
    SPOUSE = "spouse"
    SIBLING = "sibling"


class FamilyRelationship(Base):
    """Biological/legal relationships between people."""

    __tablename__ = "family_relationships"
    __table_args__ = (
        UniqueConstraint(
            "person_id",
            "related_person_id",
            "relationship_type",
            name="uq_family_relationship",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    related_person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType, name="relationship_type_enum", create_constraint=True),
        nullable=False,
    )

    # Relationships
    person: Mapped["Person"] = relationship(
        "Person",
        foreign_keys=[person_id],
        back_populates="relationships_as_person",
    )
    related_person: Mapped["Person"] = relationship(
        "Person",
        foreign_keys=[related_person_id],
        back_populates="relationships_as_related",
    )

    def __repr__(self) -> str:
        return f"<FamilyRelationship(id={self.id}, person_id={self.person_id}, related_person_id={self.related_person_id}, type='{self.relationship_type.value}')>"
