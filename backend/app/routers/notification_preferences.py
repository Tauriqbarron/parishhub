"""Notification preferences API router — N3 (#311).

CRUD for per-user, per-category, per-channel notification toggles.
Member-scoped: all endpoints require member authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.member import MemberUser, require_member
from app.database import get_db
from app.models.notification import NotificationPreference

router = APIRouter(
    prefix="/api/member/notification",
    tags=["member-notifications"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class PreferenceItem(BaseModel):
    """A single notification preference entry."""

    category: str = Field(..., description="Category: announcements, events, roster, rsvp, mass_times, sacraments")
    channel: str = Field(..., description="Channel: email, sms, app")
    enabled: bool = Field(default=True, description="Whether this category+channel is enabled")


class PreferenceItemOut(PreferenceItem):
    """Preference item returned to the client (includes id)."""

    id: int
    person_id: int


class BulkUpsertRequest(BaseModel):
    """Bulk upsert: replaces ALL preferences for the authenticated member."""

    preferences: list[PreferenceItem] = Field(
        default_factory=list,
        description="Complete list of preferences; missing entries are deleted",
    )


# ---------------------------------------------------------------------------
# GET /preferences — list all preferences for the authenticated member
# ---------------------------------------------------------------------------

@router.get(
    "/preferences",
    response_model=list[PreferenceItemOut],
    summary="List notification preferences",
)
def list_preferences(
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
) -> list[PreferenceItemOut]:
    """Return all notification preferences for the current member."""
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No person linked to this account",
        )

    prefs = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.person_id == member.person_id)
        .all()
    )

    return [
        PreferenceItemOut(
            id=p.id,
            person_id=p.person_id,
            category=p.category,
            channel=p.channel,
            enabled=p.enabled,
        )
        for p in prefs
    ]


# ---------------------------------------------------------------------------
# PUT /preferences — bulk upsert (replace all for this member)
# ---------------------------------------------------------------------------

@router.put(
    "/preferences",
    response_model=list[PreferenceItemOut],
    summary="Bulk upsert notification preferences",
)
def upsert_preferences(
    body: BulkUpsertRequest,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
) -> list[PreferenceItemOut]:
    """Replace ALL notification preferences for the current member.

    Sends a list of {category, channel, enabled}. Any existing preference
    not in the list is deleted. New entries are inserted or updated.
    """
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No person linked to this account",
        )

    person_id = member.person_id

    # 1. Delete ALL existing preferences for this person
    db.query(NotificationPreference).filter(
        NotificationPreference.person_id == person_id
    ).delete()

    # 2. Insert the submitted preferences
    results: list[NotificationPreference] = []
    for item in body.preferences:
        pref = NotificationPreference(
            person_id=person_id,
            category=item.category,
            channel=item.channel,
            enabled=item.enabled,
        )
        db.add(pref)
        results.append(pref)

    db.commit()

    # Refresh to get server-generated ids
    for pref in results:
        db.refresh(pref)

    return [
        PreferenceItemOut(
            id=p.id,
            person_id=p.person_id,
            category=p.category,
            channel=p.channel,
            enabled=p.enabled,
        )
        for p in results
    ]
