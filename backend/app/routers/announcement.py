"""Announcement CRUD API — N9 (#317).

Admin endpoints for creating, reading, updating, and deleting announcements.
On create, the announcement is saved and notification_service.emit() is called
to deliver via the specified channels (email, sms, app).

Prefix: /api/roster/announcements
Auth: require_auth (admin-only)
"""

import logging
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import User, require_auth
from app.database import get_db
from app.limiter import limiter
from app.models.ministry import Ministry
from app.models.notification import Announcement
from app.services.notifications import notification_service

logger = logging.getLogger("parish.announcements")

router = APIRouter(
    prefix="/api/roster/announcements",
    tags=["announcements"],
)

# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------


class AnnouncementCreate(BaseModel):
    """Request body for creating an announcement."""

    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1, description="Markdown body content")
    scope_type: str = Field(
        default="parish",
        pattern="^(parish|ministry)$",
        description="parish = all members, ministry = scoped to a specific ministry",
    )
    ministry_id: Optional[int] = Field(
        default=None,
        description="Required when scope_type=ministry",
    )
    channels: list[str] = Field(
        default=["app"],
        description="Delivery channels: email, sms, app",
    )


class AnnouncementUpdate(BaseModel):
    """Request body for updating an announcement."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    body: Optional[str] = Field(default=None, min_length=1)
    scope_type: Optional[str] = Field(
        default=None,
        pattern="^(parish|ministry)$",
    )
    ministry_id: Optional[int] = None
    channels: Optional[list[str]] = None


class AnnouncementResponse(BaseModel):
    """Response model for an announcement."""

    id: int
    title: str
    body: str
    scope_type: str
    ministry_id: Optional[int] = None
    channels: list
    created_by: Optional[int] = None
    sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnouncementListResponse(BaseModel):
    """Paginated list of announcements."""

    items: list[AnnouncementResponse]
    total: int
    page: int
    per_page: int


# ------------------------------------------------------------------
# Validation helper
# ------------------------------------------------------------------


def _validate_scope(data: AnnouncementCreate | AnnouncementUpdate) -> None:
    """Validate scope_type and ministry_id consistency."""
    scope = data.scope_type
    ministry = data.ministry_id

    if scope == "ministry" and not ministry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ministry_id is required when scope_type is 'ministry'",
        )
    if scope == "parish" and ministry is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ministry_id must be null when scope_type is 'parish'",
        )


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _announcement_to_response(a: Announcement) -> AnnouncementResponse:
    """Convert an ORM Announcement to a response model."""
    return AnnouncementResponse(
        id=a.id,
        title=a.title,
        body=a.body,
        scope_type=a.scope_type,
        ministry_id=a.ministry_id,
        channels=a.channels if isinstance(a.channels, list) else [],
        created_by=a.created_by,
        sent_at=a.sent_at,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


def _get_recipients_for_announcement(
    db: Session, scope_type: str, ministry_id: Optional[int]
) -> list[int]:
    """Determine the set of person_ids that should receive the announcement.

    For 'parish' scope, returns all persons (via a simple query).
    For 'ministry' scope, returns members of that ministry.
    """
    from app.models.ministry import MinistryMember
    from app.models.person import Person

    if scope_type == "ministry" and ministry_id:
        members = (
            db.query(MinistryMember)
            .filter(
                MinistryMember.ministry_id == ministry_id,
                MinistryMember.is_active == True,  # noqa: E712
            )
            .all()
        )
        return list({m.person_id for m in members})

    # Parish scope — all persons
    persons = db.query(Person).all()
    return [p.id for p in persons]


# ------------------------------------------------------------------
# POST — create announcement
# ------------------------------------------------------------------


@router.post(
    "",
    response_model=AnnouncementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new announcement",
)
@limiter.limit("30/minute")
async def create_announcement(
    request: Request,
    data: AnnouncementCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_auth)],
) -> AnnouncementResponse:
    """Admin creates an announcement and triggers delivery."""
    _validate_scope(data)

    # Validate ministry exists if scope is ministry
    if data.scope_type == "ministry" and data.ministry_id:
        ministry = db.query(Ministry).filter(Ministry.id == data.ministry_id).first()
        if not ministry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ministry with id {data.ministry_id} not found",
            )

    # Create announcement record
    now = datetime.now(timezone.utc)

    # Look up person_id from user email
    from app.models.person import Person
    person = db.query(Person).filter(Person.email == user.email).first()
    created_by = person.id if person else None

    announcement = Announcement(
        title=data.title,
        body=data.body,
        scope_type=data.scope_type,
        ministry_id=data.ministry_id,
        channels=data.channels,
        created_by=created_by,
        sent_at=now,
        created_at=now,
        updated_at=now,
    )
    db.add(announcement)
    db.flush()  # Get the announcement ID for the notification

    # Determine recipients and emit notification
    recipients = _get_recipients_for_announcement(
        db, data.scope_type, data.ministry_id
    )

    if recipients:
        notification_service.emit(
            event_type="announcement",
            recipients=recipients,
            category="announcement",
            template_data={
                "title": data.title,
                "body": data.body,
                "announcement_id": announcement.id,
                "scope_type": data.scope_type,
            },
            channels=data.channels,
            db=db,
        )

    db.commit()
    db.refresh(announcement)

    logger.info(
        "announcement_created: id=%d title=%r scope=%s recipients=%d channels=%s",
        announcement.id,
        announcement.title,
        announcement.scope_type,
        len(recipients),
        data.channels,
    )

    return _announcement_to_response(announcement)


# ------------------------------------------------------------------
# GET — list announcements
# ------------------------------------------------------------------


@router.get(
    "",
    response_model=AnnouncementListResponse,
    summary="List announcements",
)
@limiter.limit("60/minute")
async def list_announcements(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    scope_type: Annotated[Optional[str], Query(pattern="^(parish|ministry)$")] = None,
    ministry_id: Annotated[Optional[int], Query()] = None,
) -> AnnouncementListResponse:
    """List announcements with optional scope filtering."""
    query = db.query(Announcement)

    if scope_type:
        query = query.filter(Announcement.scope_type == scope_type)
    if ministry_id is not None:
        query = query.filter(Announcement.ministry_id == ministry_id)

    total = query.count()
    offset = (page - 1) * per_page
    items = (
        query.order_by(Announcement.created_at.desc())
        .offset(offset)
        .limit(per_page)
        .all()
    )

    return AnnouncementListResponse(
        items=[_announcement_to_response(a) for a in items],
        total=total,
        page=page,
        per_page=per_page,
    )


# ------------------------------------------------------------------
# GET — single announcement
# ------------------------------------------------------------------


@router.get(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    summary="Get an announcement by ID",
)
@limiter.limit("60/minute")
async def get_announcement(
    request: Request,
    announcement_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_auth)],
) -> AnnouncementResponse:
    """Retrieve a single announcement by its ID."""
    announcement = (
        db.query(Announcement)
        .filter(Announcement.id == announcement_id)
        .first()
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Announcement with id {announcement_id} not found",
        )

    return _announcement_to_response(announcement)


# ------------------------------------------------------------------
# PUT — update announcement
# ------------------------------------------------------------------


@router.put(
    "/{announcement_id}",
    response_model=AnnouncementResponse,
    summary="Update an announcement",
)
@limiter.limit("30/minute")
async def update_announcement(
    request: Request,
    announcement_id: int,
    data: AnnouncementUpdate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_auth)],
) -> AnnouncementResponse:
    """Admin updates an existing announcement."""
    announcement = (
        db.query(Announcement)
        .filter(Announcement.id == announcement_id)
        .first()
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Announcement with id {announcement_id} not found",
        )

    # Validate scope if being changed
    new_scope = data.scope_type or announcement.scope_type
    new_ministry = (
        data.ministry_id
        if data.ministry_id is not None
        else announcement.ministry_id
    )
    if new_scope == "ministry" and not new_ministry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ministry_id is required when scope_type is 'ministry'",
        )

    # Apply updates
    if data.title is not None:
        announcement.title = data.title
    if data.body is not None:
        announcement.body = data.body
    if data.scope_type is not None:
        announcement.scope_type = data.scope_type
    if data.ministry_id is not None:
        announcement.ministry_id = data.ministry_id
    if data.channels is not None:
        announcement.channels = data.channels

    announcement.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(announcement)

    logger.info(
        "announcement_updated: id=%d title=%r",
        announcement.id,
        announcement.title,
    )

    return _announcement_to_response(announcement)


# ------------------------------------------------------------------
# DELETE — delete announcement
# ------------------------------------------------------------------


@router.delete(
    "/{announcement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an announcement",
)
@limiter.limit("30/minute")
async def delete_announcement(
    request: Request,
    announcement_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    """Admin deletes an announcement."""
    announcement = (
        db.query(Announcement)
        .filter(Announcement.id == announcement_id)
        .first()
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Announcement with id {announcement_id} not found",
        )

    db.delete(announcement)
    db.commit()

    logger.info(
        "announcement_deleted: id=%d title=%r",
        announcement_id,
        announcement.title,
    )
