"""SQLAlchemy models for the Centralized Notification System."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.ministry import Ministry
    from app.models.person import Person


class NotificationPreference(Base):
    """Per-user, per-category, per-channel notification toggle."""

    __tablename__ = "notification_preferences"
    __table_args__ = (
        UniqueConstraint("person_id", "category", "channel", name="uq_person_category_channel"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # announcements, events, roster, rsvp, mass_times, sacraments
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    # email, sms, app
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    person: Mapped["Person"] = relationship("Person")

    def __repr__(self) -> str:
        return (
            f"<NotificationPreference(person_id={self.person_id}, "
            f"category='{self.category}', channel='{self.channel}', enabled={self.enabled})>"
        )


class NotificationDelivery(Base):
    """Audit trail of every notification sent/delivered."""

    __tablename__ = "notification_deliveries"
    __table_args__ = (
        Index("ix_deliveries_person_read", "person_id", "read_at"),
        Index("ix_deliveries_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued")
    # queued, sent, delivered, failed, read
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    provider_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    person: Mapped["Person"] = relationship("Person")

    def __repr__(self) -> str:
        return (
            f"<NotificationDelivery(id={self.id}, person_id={self.person_id}, "
            f"event_type='{self.event_type}', channel='{self.channel}', status='{self.status}')>"
        )


class ReminderLog(Base):
    """Deduplication log — prevents double-sending reminders."""

    __tablename__ = "reminder_log"
    __table_args__ = (
        UniqueConstraint(
            "reminder_type", "trigger_entity_type", "trigger_entity_id",
            "hours_before", "fired_at",
            name="uq_reminder_dedup",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reminder_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # event, roster, rsvp_deadline, mass_time, sacrament
    trigger_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger_entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    hours_before: Mapped[int] = mapped_column(Integer, nullable=False)
    fired_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    recipients_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return (
            f"<ReminderLog(type='{self.reminder_type}', entity={self.trigger_entity_type}#{self.trigger_entity_id}, "
            f"hours_before={self.hours_before})>"
        )


class Announcement(Base):
    """Manual broadcast from admins/leaders."""

    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)  # markdown
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False, default="parish")
    # parish, ministry
    ministry_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ministries.id", ondelete="SET NULL"), nullable=True
    )
    channels: Mapped[dict] = mapped_column(JSONB, nullable=False, default=list)
    # ["email", "sms", "app"]
    created_by: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    ministry: Mapped[Optional["Ministry"]] = relationship("Ministry")
    creator: Mapped[Optional["Person"]] = relationship("Person")

    def __repr__(self) -> str:
        return f"<Announcement(id={self.id}, title='{self.title}', scope='{self.scope_type}')>"
