"""SQLAlchemy models for the Ministries module."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.person import Person


class Ministry(Base):
    """A church ministry (e.g. Choir, Youth Group, Bible Study)."""

    __tablename__ = "ministries"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    leader_id: Mapped[Optional[int]] = mapped_column(
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
    leader: Mapped[Optional["Person"]] = relationship(
        "Person", foreign_keys=[leader_id]
    )
    members: Mapped[list["MinistryMember"]] = relationship(
        "MinistryMember", back_populates="ministry", cascade="all, delete-orphan"
    )
    events: Mapped[list["MinistryEvent"]] = relationship(
        "MinistryEvent", back_populates="ministry", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Ministry(id={self.id}, name='{self.name}')>"


class MinistryMember(Base):
    """Junction table linking persons to ministries with role."""

    __tablename__ = "ministry_members"
    __table_args__ = (
        UniqueConstraint("ministry_id", "person_id", name="uq_ministry_person"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    ministry_id: Mapped[int] = mapped_column(
        ForeignKey("ministries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    joined_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    ministry: Mapped["Ministry"] = relationship("Ministry", back_populates="members")
    person: Mapped["Person"] = relationship(
        "Person", foreign_keys=[person_id]
    )

    def __repr__(self) -> str:
        return (
            f"<MinistryMember(id={self.id}, ministry_id={self.ministry_id}, "
            f"person_id={self.person_id}, role='{self.role}')>"
        )


class MinistryEvent(Base):
    """An event organised by a ministry."""

    __tablename__ = "ministry_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    ministry_id: Mapped[int] = mapped_column(
        ForeignKey("ministries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "19:00"
    end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)    # "21:00"
    event_type: Mapped[str] = mapped_column(String(50), default="other", nullable=False)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # null = unlimited
    recurrence_rule: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # RRULE
    recurrence_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    ministry: Mapped["Ministry"] = relationship("Ministry", back_populates="events")
    attendance: Mapped[list["MinistryEventAttendance"]] = relationship(
        "MinistryEventAttendance", back_populates="event", cascade="all, delete-orphan"
    )
    rsvps: Mapped[list["EventRSVP"]] = relationship(
        "EventRSVP", back_populates="event", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<MinistryEvent(id={self.id}, title='{self.title}')>"


class MinistryEventAttendance(Base):
    """Attendance record for a person at a ministry event."""

    __tablename__ = "ministry_event_attendance"
    __table_args__ = (
        UniqueConstraint("event_id", "person_id", name="uq_event_person"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("ministry_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    attended: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    event: Mapped["MinistryEvent"] = relationship(
        "MinistryEvent", back_populates="attendance"
    )
    person: Mapped["Person"] = relationship(
        "Person", foreign_keys=[person_id]
    )

    def __repr__(self) -> str:
        return (
            f"<MinistryEventAttendance(id={self.id}, event_id={self.event_id}, "
            f"person_id={self.person_id}, attended={self.attended})>"
        )


class EventRSVP(Base):
    """RSVP status for a person at a ministry event."""

    __tablename__ = "event_rsvps"
    __table_args__ = (
        UniqueConstraint("event_id", "person_id", name="uq_event_rsvp_person"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("ministry_events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # going, not_going, maybe
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    event: Mapped["MinistryEvent"] = relationship("MinistryEvent", back_populates="rsvps")
    person: Mapped["Person"] = relationship("Person", foreign_keys=[person_id])

    def __repr__(self) -> str:
        return (
            f"<EventRSVP(id={self.id}, event_id={self.event_id}, "
            f"person_id={self.person_id}, status='{self.status}')>"
        )


class UserRole(Base):
    """Role-based access control for the Ministries platform.

    Global roles (priest, admin): ministry_id is NULL.
    Scoped roles (leader, member): ministry_id points to the specific ministry.
    """

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint(
            "user_email", "role", "ministry_id", name="uq_user_role_ministry"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    ministry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ministries.id", ondelete="CASCADE"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    ministry: Mapped[Optional["Ministry"]] = relationship("Ministry")

    def __repr__(self) -> str:
        scope = f"ministry_id={self.ministry_id}" if self.ministry_id else "global"
        return (
            f"<UserRole(id={self.id}, email='{self.user_email}', "
            f"role='{self.role}', {scope})>"
        )
