"""Notification delivery API + WebSocket stub — N4 (#312).

Endpoints for listing, marking read, and counting unread notifications.
Also provides a WebSocket endpoint stub for future real-time delivery.
Member-scoped: all endpoints require member authentication.
"""

import logging
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.member import MemberUser, require_member
from app.database import get_db
from app.models.notification import NotificationDelivery
from app.services.notifications import notification_service

logger = logging.getLogger("parish.notifications")

router = APIRouter(
    prefix="/api/member/notification",
    tags=["member-notifications"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class DeliveryOut(BaseModel):
    """Single notification delivery returned to the client."""

    id: int
    category: str
    event_type: str
    channel: str
    status: str
    title: str
    body: Optional[str] = None
    metadata: Optional[dict] = None
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DeliveryPage(BaseModel):
    """Paginated list of notification deliveries."""

    items: list[DeliveryOut]
    total: int
    page: int
    page_size: int


class MarkReadRequest(BaseModel):
    """Body for marking deliveries as read."""

    delivery_ids: list[int] = Field(..., min_length=1, description="IDs of deliveries to mark as read")


class MarkReadResponse(BaseModel):
    """Response after marking deliveries as read."""

    updated: int


class UnreadCountResponse(BaseModel):
    """Response with unread count."""

    total: int


# ---------------------------------------------------------------------------
# GET /deliveries?status=unread — paginated list
# ---------------------------------------------------------------------------

@router.get(
    "/deliveries",
    response_model=DeliveryPage,
    summary="List notification deliveries",
)
def list_deliveries(
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g., 'unread')"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> DeliveryPage:
    """Return paginated notification deliveries for the current member.

    Use ?status=unread to show only unread deliveries.
    Most recent deliveries are returned first.
    """
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No person linked to this account",
        )

    query = db.query(NotificationDelivery).filter(
        NotificationDelivery.person_id == member.person_id
    )

    if status_filter == "unread":
        query = query.filter(NotificationDelivery.read_at.is_(None))

    total = query.count()
    deliveries = (
        query.order_by(NotificationDelivery.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return DeliveryPage(
        items=[
            DeliveryOut(
                id=d.id,
                category=d.category,
                event_type=d.event_type,
                channel=d.channel,
                status=d.status,
                title=d.title,
                body=d.body,
                metadata=d.metadata_json,
                read_at=d.read_at,
                created_at=d.created_at,
            )
            for d in deliveries
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------------------------
# PUT /deliveries/mark-read — mark specific deliveries as read
# ---------------------------------------------------------------------------

@router.put(
    "/deliveries/mark-read",
    response_model=MarkReadResponse,
    summary="Mark deliveries as read",
)
def mark_deliveries_read(
    body: MarkReadRequest,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
) -> MarkReadResponse:
    """Mark one or more notification deliveries as read for the current member."""
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No person linked to this account",
        )

    updated = notification_service.mark_read(
        db=db,
        person_id=member.person_id,
        delivery_ids=body.delivery_ids,
    )
    return MarkReadResponse(updated=updated)


# ---------------------------------------------------------------------------
# GET /unread-count — badge count
# ---------------------------------------------------------------------------

@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Get unread notification count",
)
def get_unread_count(
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
) -> UnreadCountResponse:
    """Return the count of unread notification deliveries for the current member."""
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No person linked to this account",
        )

    total = notification_service.get_unread_count(
        db=db,
        person_id=member.person_id,
    )
    return UnreadCountResponse(total=total)


# ---------------------------------------------------------------------------
# WebSocket /ws — stub for real-time delivery (N6)
# ---------------------------------------------------------------------------

@router.websocket("/ws")
async def websocket_stub(websocket: WebSocket) -> None:
    """WebSocket endpoint stub for real-time notification delivery.

    Accepts connections and logs them. Full delivery implementation
    will be completed in N6 (frontend work).

    The client should connect here to receive live notifications.
    """
    client_host = websocket.client.host if websocket.client else "unknown"
    await websocket.accept()
    logger.info("notification_ws_connected: client=%s", client_host)

    try:
        # Keep the connection alive and log any incoming messages
        while True:
            data = await websocket.receive_text()
            logger.debug("notification_ws_message: client=%s data=%s", client_host, data[:200])
    except Exception:
        logger.info("notification_ws_disconnected: client=%s", client_host)
