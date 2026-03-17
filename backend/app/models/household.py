from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.person import Person


class HouseholdRole(str, PyEnum):
    HEAD = "head"
    SPOUSE = "spouse"
    CHILD = "child"
    OTHER = "other"


class Household(Base):
    """Groups people living at the same address."""

    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address_line1: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    attending_since: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    members: Mapped[list["HouseholdMember"]] = relationship(
        "HouseholdMember", back_populates="household", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Household(id={self.id}, name='{self.name}')>"


class HouseholdMember(Base):
    """Junction table linking people to households with roles."""

    __tablename__ = "household_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), nullable=False
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[HouseholdRole] = mapped_column(
        Enum(HouseholdRole, name="household_role_enum", create_constraint=True),
        nullable=False,
    )
    is_primary_household: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    household: Mapped["Household"] = relationship("Household", back_populates="members")
    person: Mapped["Person"] = relationship(
        "Person", back_populates="household_memberships"
    )

    def __repr__(self) -> str:
        return f"<HouseholdMember(id={self.id}, household_id={self.household_id}, person_id={self.person_id}, role='{self.role.value}')>"
