"""Tests for NotificationService — emit, preference gating, mark_read, unread_count."""

import pytest
from sqlalchemy.orm import Session

from app.models.notification import NotificationDelivery, NotificationPreference
from app.services.notifications import NotificationService


@pytest.fixture
def svc():
    return NotificationService()


def test_emit_creates_delivery_records(db_session: Session, svc: NotificationService):
    count = svc.emit(
        event_type="test.event",
        recipients=[1],
        category="roster",
        template_data={"title": "Test", "body": "Hello"},
        channels=["app"],
        db=db_session,
    )
    db_session.commit()
    assert count == 1
    deliveries = db_session.query(NotificationDelivery).filter_by(event_type="test.event").all()
    assert len(deliveries) == 1
    assert deliveries[0].title == "Test"


def test_emit_without_db_auto_creates_session(svc: NotificationService):
    # This creates its own session, commits internally
    count = svc.emit(
        event_type="test.auto",
        recipients=[1],
        category="roster",
        template_data={"title": "Auto Session Test"},
        channels=["app"],
    )
    assert count >= 0  # should not crash


def test_emit_raises_when_title_missing(db_session: Session, svc: NotificationService):
    with pytest.raises(ValueError, match="title"):
        svc.emit(
            event_type="test.no_title",
            recipients=[1],
            category="roster",
            template_data={"body": "No title here"},
            db=db_session,
        )


def test_preference_gating_skips_disabled(db_session: Session, svc: NotificationService):
    # Create a disabled preference
    pref = NotificationPreference(
        person_id=1, category="roster", channel="sms", enabled=False
    )
    db_session.add(pref)
    db_session.commit()

    count = svc.emit(
        event_type="test.gated",
        recipients=[1],
        category="roster",
        template_data={"title": "Gated"},
        channels=["sms"],
        db=db_session,
    )
    db_session.commit()
    assert count == 0  # skipped due to disabled pref


def test_no_preference_defaults_to_enabled(db_session: Session, svc: NotificationService):
    # No preference record at all — should default to enabled
    count = svc.emit(
        event_type="test.default",
        recipients=[1],
        category="roster",
        template_data={"title": "Default Enabled"},
        channels=["app"],
        db=db_session,
    )
    db_session.commit()
    assert count == 1


def test_mark_read(db_session: Session, svc: NotificationService):
    svc.emit(
        event_type="test.mark",
        recipients=[1],
        category="roster",
        template_data={"title": "Mark Read Test"},
        channels=["app"],
        db=db_session,
    )
    db_session.commit()
    delivery = db_session.query(NotificationDelivery).first()
    assert delivery.read_at is None

    updated = svc.mark_read(db_session, 1, [delivery.id])
    assert updated == 1
    db_session.refresh(delivery)
    assert delivery.read_at is not None


def test_get_unread_count(db_session: Session, svc: NotificationService):
    svc.emit(
        event_type="test.count",
        recipients=[1],
        category="roster",
        template_data={"title": "Count Test"},
        channels=["app"],
        db=db_session,
    )
    db_session.commit()
    assert svc.get_unread_count(db_session, 1) == 1
    assert svc.get_unread_count(db_session, 999) == 0
