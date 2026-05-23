"""Notification service — centralized notification delivery with preference gating and delivery logging.

Implements N2 (#310): full event bus with preference checks, delivery audit trail,
and helper methods for mark_read / get_unread_count.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.notification import NotificationDelivery, NotificationPreference

logger = logging.getLogger("parish.notifications")

DEFAULT_CHANNELS = ["app"]


class NotificationService:
    """Centralized notification delivery.

    Roster and other systems call emit() — this service routes to:
    - In-app (WebSocket)
    - Email (listmonk)
    - SMS (TextBee)

    Preferences are gated: each (person_id, category, channel) must be
    enabled=true, or no explicit disable (no record = enabled by default).

    emit() creates its own DB session when none is provided, making it safe
    for fire-and-forget callers like RosterEventEmitter.
    emit() does NOT commit — callers must commit after calling.
    """

    # ------------------------------------------------------------------
    # emit — fire-and-forget notification dispatch
    # ------------------------------------------------------------------

    def emit(
        self,
        event_type: str,
        recipients: list[int],
        category: str,
        template_data: dict,
        channels: Optional[list[str]] = None,
        db: Optional[Session] = None,
    ) -> int:
        """Emit a notification event.

        1. Check user preferences for category + channel
        2. Create NotificationDelivery records for each recipient+channel combo
        3. Log the event

        Creates its own DB session when db=None (fire-and-forget safe).
        Does NOT commit — callers with their own session must commit.
        Returns count of delivery records created.

        Raises ValueError if title is missing from template_data
        (prevents silent event_type-as-title fallback).
        """
        if channels is None:
            channels = DEFAULT_CHANNELS

        title = template_data.get("title")
        if not title:
            raise ValueError(
                f"emit(): 'title' is required in template_data for event_type='{event_type}'"
            )
        body = template_data.get("body") or ""

        own_session = db is None
        if own_session:
            db = SessionLocal()

        try:
            delivered_count = 0
            for person_id in recipients:
                for channel in channels:
                    # ---- Preference gating ----
                    pref = (
                        db.query(NotificationPreference)
                        .filter(
                            NotificationPreference.person_id == person_id,
                            NotificationPreference.category == category,
                            NotificationPreference.channel == channel,
                        )
                        .first()
                    )
                    if pref is not None and not pref.enabled:
                        logger.debug(
                            "notification_skipped: person=%d category=%s channel=%s — disabled",
                            person_id, category, channel,
                        )
                        continue

                    # ---- Create delivery record ----
                    delivery = NotificationDelivery(
                        person_id=person_id,
                        category=category,
                        event_type=event_type,
                        channel=channel,
                        status="queued",
                        title=title,
                        body=body,
                        metadata_json=template_data,
                    )
                    db.add(delivery)
                    delivered_count += 1

            if own_session:
                db.commit()

            logger.info(
                "notification_emit: type=%s category=%s recipients=%d channels=%s deliveries=%d",
                event_type, category, len(recipients), channels, delivered_count,
            )
            return delivered_count
        except Exception:
            if own_session:
                db.rollback()
            raise
        finally:
            if own_session:
                db.close()

    # ------------------------------------------------------------------
    # mark_read — mark deliveries as read for a person
    # ------------------------------------------------------------------

    def mark_read(self, db: Session, person_id: int, delivery_ids: list[int]) -> int:
        """Mark deliveries as read. Returns count of updated records."""
        if not delivery_ids:
            return 0

        now = datetime.now(timezone.utc)
        updated = (
            db.query(NotificationDelivery)
            .filter(
                NotificationDelivery.id.in_(delivery_ids),
                NotificationDelivery.person_id == person_id,
            )
            .update({"read_at": now, "status": "read"}, synchronize_session=False)
        )
        db.commit()
        logger.info("notification_mark_read: person=%d count=%d", person_id, updated)
        return updated

    # ------------------------------------------------------------------
    # get_unread_count — badge count
    # ------------------------------------------------------------------

    def get_unread_count(self, db: Session, person_id: int) -> int:
        """Return count of unread notifications for badge display."""
        return (
            db.query(NotificationDelivery)
            .filter(
                NotificationDelivery.person_id == person_id,
                NotificationDelivery.read_at.is_(None),
            )
            .count()
        )


# Singleton — shared across all services
notification_service = NotificationService()
