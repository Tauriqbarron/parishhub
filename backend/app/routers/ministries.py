"""API router for Ministry CRUD operations with RBAC."""

from datetime import date
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.auth.dependencies import User, require_auth
from app.auth.roles import require_role
from app.database import get_db
from app.limiter import limiter
from app.schemas.ministry import (
    AttendanceBatchCreate,
    AttendanceResponse,
    CalendarEventResponse,
    LeaderInfo,
    MinistryCreate,
    MinistryDetailResponse,
    MinistryEventCreate,
    MinistryEventResponse,
    MinistryEventUpdate,
    MinistryMemberCreate,
    MinistryMemberResponse,
    MinistryMemberUpdate,
    MinistryResponse,
    MinistryUpdate,
    UserRoleResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.services.ministry import MinistryService, MinistryValidationError, get_ministry_service

router = APIRouter(prefix="/api/ministries", tags=["ministries"])
persons_router = APIRouter(prefix="/api/persons", tags=["persons"])


# ---------------------------------------------------------------------------
# Ministry CRUD
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=MinistryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ministry",
)
@limiter.limit("30/minute")
async def create_ministry(
    request: Request,
    data: MinistryCreate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_role("priest", "admin"))],
) -> MinistryResponse:
    try:
        ministry = service.create_ministry(data)
        return MinistryResponse.model_validate(ministry)
    except MinistryValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "",
    response_model=PaginatedResponse[MinistryResponse],
    summary="List ministries",
)
@limiter.limit("60/minute")
async def list_ministries(
    request: Request,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[Optional[str], Query()] = None,
    is_active: Annotated[Optional[bool], Query()] = None,
    sort_by: Annotated[str, Query(pattern="^(name|created_at|updated_at)$")] = "name",
    sort_order: Annotated[str, Query(pattern="^(asc|desc)$")] = "asc",
) -> PaginatedResponse[MinistryResponse]:
    items, total = service.list_ministries(
        page, per_page, search, is_active, sort_by, sort_order
    )
    # Add member_count
    responses = []
    for m in items:
        r = MinistryResponse.model_validate(m)
        r.member_count = sum(1 for mb in m.members if mb.is_active) if hasattr(m, "members") and m.members else 0
        responses.append(r)

    return PaginatedResponse.create(items=responses, total=total, page=page, per_page=per_page)


@router.get(
    "/statistics",
    response_model=dict[str, Any],
    summary="Get ministry statistics",
)
@limiter.limit("60/minute")
async def get_statistics(
    request: Request,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_role("priest", "admin"))],
) -> dict[str, Any]:
    return service.get_statistics()


@router.get(
    "/my-roles",
    response_model=list[UserRoleResponse],
    summary="Get current user's roles",
)
@limiter.limit("60/minute")
async def get_my_roles(
    request: Request,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[UserRoleResponse]:
    from app.models.ministry import UserRole
    db = next(get_db())
    roles = db.query(UserRole).filter(UserRole.user_email == user.email).all()
    return [UserRoleResponse.model_validate(r) for r in roles]


@router.get(
    "/{ministry_id}",
    response_model=MinistryDetailResponse,
    summary="Get ministry detail with members and events",
)
@limiter.limit("60/minute")
async def get_ministry(
    request: Request,
    ministry_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MinistryDetailResponse:
    ministry = service.get_ministry_detail(ministry_id)
    if not ministry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ministry not found")
    resp = MinistryDetailResponse.model_validate(ministry)
    resp.member_count = len(ministry.members) if ministry.members else 0
    # Populate person_name on members from loaded relationship
    for i, member in enumerate(ministry.members):
        if member.person:
            resp.members[i].person_name = f"{member.person.first_name} {member.person.last_name}"
    if ministry.leader:
        resp.leader = LeaderInfo(
            id=ministry.leader.id,
            first_name=ministry.leader.first_name,
            last_name=ministry.leader.last_name,
            email=ministry.leader.email,
        )
    return resp


@router.put(
    "/{ministry_id}",
    response_model=MinistryResponse,
    summary="Update a ministry",
)
@limiter.limit("30/minute")
async def update_ministry(
    request: Request,
    ministry_id: int,
    data: MinistryUpdate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_role("priest", "admin"))],
) -> MinistryResponse:
    ministry = service.update_ministry(ministry_id, data)
    if not ministry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ministry not found")
    return MinistryResponse.model_validate(ministry)


@router.delete(
    "/{ministry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ministry (soft delete if has members/events)",
)
@limiter.limit("30/minute")
async def delete_ministry(
    request: Request,
    ministry_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_role("priest", "admin"))],
) -> None:
    if not service.delete_ministry(ministry_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ministry not found")


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------
@router.post(
    "/{ministry_id}/members",
    response_model=MinistryMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to a ministry",
)
@limiter.limit("30/minute")
async def add_member(
    request: Request,
    ministry_id: int,
    data: MinistryMemberCreate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MinistryMemberResponse:
    # Override ministry_id from URL
    data.ministry_id = ministry_id
    try:
        member = service.add_member(data)
        resp = MinistryMemberResponse.model_validate(member)
        if member.person:
            resp.person_name = f"{member.person.first_name} {member.person.last_name}"
        return resp
    except MinistryValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/{ministry_id}/members/{person_id}",
    response_model=MinistryMemberResponse,
    summary="Update a member's role",
)
@limiter.limit("30/minute")
async def update_member(
    request: Request,
    ministry_id: int,
    person_id: int,
    data: MinistryMemberUpdate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MinistryMemberResponse:
    member = service.update_member(ministry_id, person_id, data)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    resp = MinistryMemberResponse.model_validate(member)
    if member.person:
        resp.person_name = f"{member.person.first_name} {member.person.last_name}"
    return resp


@router.delete(
    "/{ministry_id}/members/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a ministry",
)
@limiter.limit("30/minute")
async def remove_member(
    request: Request,
    ministry_id: int,
    person_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    if not service.remove_member(ministry_id, person_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
@router.post(
    "/{ministry_id}/events",
    response_model=MinistryEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ministry event",
)
@limiter.limit("30/minute")
async def create_event(
    request: Request,
    ministry_id: int,
    data: MinistryEventCreate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MinistryEventResponse:
    data.ministry_id = ministry_id
    try:
        event = service.create_event(data)
        return MinistryEventResponse.model_validate(event)
    except MinistryValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/{ministry_id}/events",
    response_model=list[MinistryEventResponse],
    summary="List events for a ministry",
)
@limiter.limit("60/minute")
async def list_events(
    request: Request,
    ministry_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
) -> list[MinistryEventResponse]:
    events = service.list_events(ministry_id, date_from, date_to)
    return [MinistryEventResponse.model_validate(e) for e in events]


@router.put(
    "/{ministry_id}/events/{event_id}",
    response_model=MinistryEventResponse,
    summary="Update a ministry event",
)
@limiter.limit("30/minute")
async def update_event(
    request: Request,
    ministry_id: int,
    event_id: int,
    data: MinistryEventUpdate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MinistryEventResponse:
    event = service.update_event(event_id, data)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return MinistryEventResponse.model_validate(event)


@router.delete(
    "/{ministry_id}/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ministry event",
)
@limiter.limit("30/minute")
async def delete_event(
    request: Request,
    ministry_id: int,
    event_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    if not service.delete_event(event_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
@router.post(
    "/{ministry_id}/events/{event_id}/attendance",
    response_model=dict[str, int],
    summary="Record attendance for an event",
)
@limiter.limit("30/minute")
async def record_attendance(
    request: Request,
    ministry_id: int,
    event_id: int,
    data: AttendanceBatchCreate,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> dict[str, int]:
    try:
        count = service.record_attendance(event_id, data.person_ids)
        return {"recorded": count}
    except MinistryValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/{ministry_id}/events/{event_id}/attendance",
    response_model=list[AttendanceResponse],
    summary="Get attendance for an event",
)
@limiter.limit("60/minute")
async def get_attendance(
    request: Request,
    ministry_id: int,
    event_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[AttendanceResponse]:
    records = service.get_attendance(event_id)
    results = []
    for r in records:
        resp = AttendanceResponse.model_validate(r)
        if r.person:
            resp.person_name = f"{r.person.first_name} {r.person.last_name}"
        results.append(resp)
    return results


# ---------------------------------------------------------------------------
# Person-nested
# ---------------------------------------------------------------------------
@persons_router.get(
    "/{person_id}/ministries",
    response_model=list[MinistryMemberResponse],
    summary="Get all ministries for a person",
    tags=["ministries"],
)
@limiter.limit("60/minute")
async def get_person_ministries(
    request: Request,
    person_id: int,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[MinistryMemberResponse]:
    memberships = service.get_person_ministries(person_id)
    results = []
    for m in memberships:
        resp = MinistryMemberResponse.model_validate(m)
        if m.ministry:
            resp.person_name = m.ministry.name
        results.append(resp)
    return results


# ---------------------------------------------------------------------------
# Calendar — cross-ministry events
# ---------------------------------------------------------------------------
calendar_router = APIRouter(prefix="/api", tags=["calendar"])


@calendar_router.get(
    "/events",
    response_model=list[CalendarEventResponse],
    summary="List all events across ministries (for calendar view)",
)
@limiter.limit("60/minute")
async def list_all_events(
    request: Request,
    service: Annotated[MinistryService, Depends(get_ministry_service)],
    user: Annotated[User, Depends(require_auth)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
    ministry_id: Annotated[Optional[int], Query()] = None,
) -> list[CalendarEventResponse]:
    rows = service.list_all_events(date_from, date_to, ministry_id)
    results = []
    for event, ministry_name in rows:
        resp = CalendarEventResponse.model_validate(event)
        resp.ministry_name = ministry_name
        results.append(resp)
    return results
