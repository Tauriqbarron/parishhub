from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.household import HouseholdMember
    from app.models.relationship import FamilyRelationship
    from app.models.sacrament import Sacrament
    from app.models.death import Death


class Gender(str, PyEnum):
    MALE = "male"
    FEMALE = "female"


class Person(Base):
    """Primary entity for all parishioners."""

    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, index=True
    )
    gender: Mapped[Optional[Gender]] = mapped_column(
        Enum(Gender, name="gender_enum", create_constraint=True),
        nullable=True,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    household_memberships: Mapped[list["HouseholdMember"]] = relationship(
        "HouseholdMember", back_populates="person", cascade="all, delete-orphan"
    )
    sacraments: Mapped[list["Sacrament"]] = relationship(
        "Sacrament",
        foreign_keys="Sacrament.person_id",
        back_populates="person",
        cascade="all, delete-orphan",
    )
    relationships_as_person: Mapped[list["FamilyRelationship"]] = relationship(
        "FamilyRelationship",
        foreign_keys="FamilyRelationship.person_id",
        back_populates="person",
        cascade="all, delete-orphan",
    )
    relationships_as_related: Mapped[list["FamilyRelationship"]] = relationship(
        "FamilyRelationship",
        foreign_keys="FamilyRelationship.related_person_id",
        back_populates="related_person",
        cascade="all, delete-orphan",
    )
    death: Mapped[Optional["Death"]] = relationship(
        "Death",
        foreign_keys="Death.person_id",
        back_populates="person",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Person(id={self.id}, name='{self.first_name} {self.last_name}')>"
