"""SQLAlchemy models for the Roster System."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, String, Text,
    UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.ministry import Ministry, MinistryEvent
    from app.models.mass_times import MassTime
    from app.models.person import Person


# ---------------------------------------------------------------------------
# RosterRole — parish-defined capability badges
# ---------------------------------------------------------------------------
class RosterRole(Base):
    """A capability badge assigned to persons (e.g. Reader, Usher, Sacristan)."""

    __tablename__ = "roster_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    persons: Mapped[list["PersonRosterRole"]] = relationship(
        "PersonRosterRole", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RosterRole(id={self.id}, name='{self.name}')>"


# ---------------------------------------------------------------------------
# PersonRosterRole — join: which roles a person holds
# ---------------------------------------------------------------------------
class PersonRosterRole(Base):
    """Links a person to a roster role they are qualified for."""

    __tablename__ = "person_roster_roles"
    __table_args__ = (
        UniqueConstraint("person_id", "role_id", name="uq_person_roster_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roster_roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    person: Mapped["Person"] = relationship("Person", foreign_keys=[person_id])
    role: Mapped["RosterRole"] = relationship("RosterRole", back_populates="persons")

    def __repr__(self) -> str:
        return f"<PersonRosterRole(person_id={self.person_id}, role_id={self.role_id})>"


# ---------------------------------------------------------------------------
# RosterTemplate — blueprint for generating roster instances
# ---------------------------------------------------------------------------
class RosterTemplate(Base):
    """A reusable roster template (e.g. 'Sunday 9am Mass')."""

    __tablename__ = "roster_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ministry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ministries.id", ondelete="CASCADE"), nullable=True, index=True
    )
    mass_time_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("mass_times.id", ondelete="SET NULL"), nullable=True
    )
    event_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ministry_events.id", ondelete="SET NULL"), nullable=True
    )
    recurrence_rule: Mapped[str] = mapped_column(
        String(20), nullable=False, default="none"
    )  # none, weekly, biweekly, monthly
    recurrence_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    settings: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    # settings shape: {
    #   "keep_assignee": bool,
    #   "auto_open_hours": int,
    #   "reminder_hours": [int],
    #   "allow_self_assign": bool
    # }
    created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    ministry: Mapped[Optional["Ministry"]] = relationship("Ministry")
    mass_time: Mapped[Optional["MassTime"]] = relationship("MassTime")
    event: Mapped[Optional["MinistryEvent"]] = relationship("MinistryEvent")
    slots: Mapped[list["RosterTemplateSlot"]] = relationship(
        "RosterTemplateSlot", back_populates="template", cascade="all, delete-orphan"
    )
    instances: Mapped[list["RosterInstance"]] = relationship(
        "RosterInstance", back_populates="template", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RosterTemplate(id={self.id}, name='{self.name}')>"


# ---------------------------------------------------------------------------
# RosterTemplateSlot — a single slot in a template
# ---------------------------------------------------------------------------
class RosterTemplateSlot(Base):
    """A slot definition within a roster template (e.g. '1st Reading')."""

    __tablename__ = "roster_template_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("roster_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roster_roles.id", ondelete="RESTRICT"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    min_persons: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_persons: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    template: Mapped["RosterTemplate"] = relationship(
        "RosterTemplate", back_populates="slots"
    )
    role: Mapped["RosterRole"] = relationship("RosterRole")

    def __repr__(self) -> str:
        return f"<RosterTemplateSlot(id={self.id}, label='{self.label}')>"


# ---------------------------------------------------------------------------
# RosterInstance — a generated roster for a specific date
# ---------------------------------------------------------------------------
class RosterInstance(Base):
    """A concrete roster instance for a specific date."""

    __tablename__ = "roster_instances"

    id: Mapped[int] = mapped_column(primary_key=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("roster_templates.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft"
    )  # draft, published, completed, cancelled
    generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    archived_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    template: Mapped["RosterTemplate"] = relationship(
        "RosterTemplate", back_populates="instances"
    )
    assignments: Mapped[list["RosterAssignment"]] = relationship(
        "RosterAssignment", back_populates="instance", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<RosterInstance(id={self.id}, template_id={self.template_id}, date={self.date})>"

    @property
    def slot_count(self) -> int:
        return len(self.template.slots) if self.template else 0

    @property
    def template_name(self) -> Optional[str]:
        return self.template.name if self.template else None


# ---------------------------------------------------------------------------
# RosterAssignment — a person assigned to a slot in an instance
# ---------------------------------------------------------------------------
class RosterAssignment(Base):
    """A person filling a roster slot on a specific date."""

    __tablename__ = "roster_assignments"
    __table_args__ = (
        UniqueConstraint("instance_id", "slot_id", "person_id", name="uq_instance_slot_person"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    instance_id: Mapped[int] = mapped_column(
        ForeignKey("roster_instances.id", ondelete="CASCADE"), nullable=False, index=True
    )
    slot_id: Mapped[int] = mapped_column(
        ForeignKey("roster_template_slots.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, accepted, declined, completed, cancelled
    assigned_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    declined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    instance: Mapped["RosterInstance"] = relationship(
        "RosterInstance", back_populates="assignments"
    )
    slot: Mapped["RosterTemplateSlot"] = relationship("RosterTemplateSlot")
    person: Mapped["Person"] = relationship("Person", foreign_keys=[person_id])

    def __repr__(self) -> str:
        return (
            f"<RosterAssignment(id={self.id}, instance_id={self.instance_id}, "
            f"person_id={self.person_id}, status='{self.status}')>"
        )

    @property
    def person_name(self) -> Optional[str]:
        if self.person:
            return f"{self.person.first_name} {self.person.last_name}"
        return None

    @property
    def template_name(self) -> Optional[str]:
        if self.instance and self.instance.template:
            return self.instance.template.name
        return None

    @property
    def slot_label(self) -> Optional[str]:
        return self.slot.label if self.slot else None

    @property
    def role_name(self) -> Optional[str]:
        return self.slot.role.name if self.slot and self.slot.role else None

    @property
    def instance_date(self) -> Optional[str]:
        return self.instance.date.isoformat() if self.instance and self.instance.date else None


# ---------------------------------------------------------------------------
# RosterSwapRequest — peer-to-peer swap proposals
# ---------------------------------------------------------------------------
class RosterSwapRequest(Base):
    """A proposed swap between two people for a roster assignment."""

    __tablename__ = "roster_swap_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("roster_assignments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    to_person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, accepted, declined, cancelled
    requested_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    assignment: Mapped["RosterAssignment"] = relationship("RosterAssignment")
    from_person: Mapped["Person"] = relationship("Person", foreign_keys=[from_person_id])
    to_person: Mapped["Person"] = relationship("Person", foreign_keys=[to_person_id])

    def __repr__(self) -> str:
        return (
            f"<RosterSwapRequest(id={self.id}, assignment_id={self.assignment_id}, "
            f"from={self.from_person_id}, to={self.to_person_id}, status='{self.status}')>"
        )
