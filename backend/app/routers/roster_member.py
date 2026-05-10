"""API router for member-facing roster operations."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.member import MemberUser, require_member
from app.schemas.roster import (
    RosterAssignmentResponse,
    RosterInstanceCreate,
    RosterInstanceResponse,
    RosterSwapCreate,
    RosterSwapResponse,
    RosterTemplateResponse,
)
from app.services.roster import RosterService, RosterValidationError, get_roster_service

router = APIRouter(prefix="/api/member/roster", tags=["member-roster"])


# ---------------------------------------------------------------------------
# My Assignments
# ---------------------------------------------------------------------------
@router.get(
    "/my",
    response_model=list[RosterAssignmentResponse],
    summary="Get my roster assignments",
)
async def get_my_assignments(
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
) -> list[RosterAssignmentResponse]:
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member account not linked to a person record",
        )
    assignments = service.get_my_assignments(member.person_id, date_from, date_to)
    return [RosterAssignmentResponse.model_validate(a) for a in assignments]


# ---------------------------------------------------------------------------
# Ministry-scoped Instances
# ---------------------------------------------------------------------------
@router.get(
    "/ministry/{ministry_id}",
    response_model=list[RosterInstanceResponse],
    summary="List roster instances for a ministry (member must belong to it)",
)
async def list_ministry_instances(
    ministry_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
) -> list[RosterInstanceResponse]:
    # Verify member belongs to this ministry
    member_ministry_ids = {r["ministry_id"] for r in member.roles if r.get("ministry_id")}
    if ministry_id not in member_ministry_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this ministry",
        )
    instances = service.list_instances(date_from, date_to, ministry_id)
    return [RosterInstanceResponse.model_validate(i) for i in instances]


# ---------------------------------------------------------------------------
# Instance Detail (member view)
# ---------------------------------------------------------------------------
@router.get(
    "/instances/{instance_id}",
    response_model=RosterInstanceResponse,
    summary="Get a roster instance (member view)",
)
async def get_instance(
    instance_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterInstanceResponse:
    try:
        instance = service.get_instance(instance_id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# ---------------------------------------------------------------------------
# Self-Assign
# ---------------------------------------------------------------------------
@router.post(
    "/instances/{instance_id}/self-assign",
    response_model=RosterAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Self-assign to a roster slot (requires matching role)",
)
async def self_assign(
    instance_id: int,
    slot_id: Annotated[int, Query()],
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterAssignmentResponse:
    if member.person_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member account not linked to a person record",
        )
    try:
        assignment = service.self_assign(instance_id, slot_id, member.person_id)
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        if e.detail.get("missing_role"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the required roster role for this slot",
            )
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)


# ---------------------------------------------------------------------------
# Assignment Status Actions
# ---------------------------------------------------------------------------
@router.put(
    "/assignments/{assignment_id}/accept",
    response_model=RosterAssignmentResponse,
    summary="Accept a roster assignment",
)
async def accept_assignment(
    assignment_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterAssignmentResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        assignment = service.update_assignment_status(
            assignment_id, "accepted", member.person_id
        )
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/assignments/{assignment_id}/decline",
    response_model=RosterAssignmentResponse,
    summary="Decline a roster assignment",
)
async def decline_assignment(
    assignment_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterAssignmentResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        assignment = service.update_assignment_status(
            assignment_id, "declined", member.person_id
        )
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/assignments/{assignment_id}/complete",
    response_model=RosterAssignmentResponse,
    summary="Mark a roster assignment as completed",
)
async def complete_assignment(
    assignment_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterAssignmentResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        assignment = service.update_assignment_status(
            assignment_id, "completed", member.person_id
        )
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/assignments/{assignment_id}/cancel",
    response_model=RosterAssignmentResponse,
    summary="Cancel own roster assignment",
)
async def cancel_assignment(
    assignment_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterAssignmentResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        assignment = service.cancel_assignment(assignment_id, member.person_id)
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


# ---------------------------------------------------------------------------
# Swap Operations
# ---------------------------------------------------------------------------
@router.post(
    "/instances",
    response_model=RosterInstanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a roster instance from a template (leader/admin only)",
)
async def create_instance(
    data: RosterInstanceCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterInstanceResponse:
    """Create a roster instance from a template. Only group leaders/admins of the
    template's ministry can create instances."""
    # Verify the template exists and get its ministry
    template = service.get_template(data.template_id)
    if template.ministry_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template has no ministry — cannot create from member portal",
        )

    # Check leadership for this ministry
    matching = [
        r for r in member.roles
        if r["ministry_id"] == template.ministry_id and r["role"] in ("leader", "admin")
    ]
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a group leader or admin of this ministry to create rosters",
        )

    try:
        instance = service.generate_instance(data.template_id, data.date)
        if data.publish:
            instance = service.publish_instance(instance.id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/templates",
    response_model=list[RosterTemplateResponse],
    summary="List roster templates for a ministry",
)
async def list_templates(
    ministry_id: Annotated[int, Query()],
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> list[RosterTemplateResponse]:
    """List active roster templates for a ministry. Member must belong to it."""
    member_ministry_ids = {r["ministry_id"] for r in member.roles if r.get("ministry_id")}
    if ministry_id not in member_ministry_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this ministry",
        )
    templates = service.list_templates(ministry_id=ministry_id, is_active=True)
    return [RosterTemplateResponse.model_validate(t) for t in templates]


@router.put(
    "/instances/{instance_id}/publish",
    response_model=RosterInstanceResponse,
    summary="Publish a draft roster instance (leader/admin only)",
)
async def publish_instance(
    instance_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterInstanceResponse:
    """Publish a draft roster instance. Only leaders/admins of the template's ministry."""
    try:
        instance = service.get_instance(instance_id)
        if instance.template and instance.template.ministry_id:
            matching = [
                r for r in member.roles
                if r["ministry_id"] == instance.template.ministry_id and r["role"] in ("leader", "admin")
            ]
            if not matching:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You must be a leader/admin of this ministry",
                )
        instance = service.publish_instance(instance_id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# ---------------------------------------------------------------------------
# Swap Operations (continued)
# ---------------------------------------------------------------------------
@router.post(
    "/assignments/{assignment_id}/swap",
    response_model=RosterSwapResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Propose a swap for a roster assignment",
)
async def propose_swap(
    assignment_id: int,
    data: RosterSwapCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterSwapResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        swap = service.propose_swap(
            assignment_id, member.person_id, data.to_person_id, data.notes
        )
        return RosterSwapResponse.model_validate(swap)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/swaps/{swap_id}/accept",
    response_model=RosterSwapResponse,
    summary="Accept a swap proposal",
)
async def accept_swap(
    swap_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterSwapResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        swap = service.accept_swap(swap_id, member.person_id)
        return RosterSwapResponse.model_validate(swap)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/swaps/{swap_id}/decline",
    response_model=RosterSwapResponse,
    summary="Decline a swap proposal",
)
async def decline_swap(
    swap_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterSwapResponse:
    if member.person_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No person linked")
    try:
        swap = service.decline_swap(swap_id, member.person_id)
        return RosterSwapResponse.model_validate(swap)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/swaps/pending",
    response_model=list[RosterSwapResponse],
    summary="Get pending swaps for current member",
)
async def get_pending_swaps(
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> list[RosterSwapResponse]:
    """Returns swaps where the current member is the recipient (to_person)."""
    if member.person_id is None:
        return []
    # Query swaps addressed to this member that are still pending
    from sqlalchemy.orm import joinedload
    from app.models.roster import RosterSwapRequest

    swaps = (
        service.db.query(RosterSwapRequest)
        .options(
            joinedload(RosterSwapRequest.assignment),
            joinedload(RosterSwapRequest.from_person),
            joinedload(RosterSwapRequest.to_person),
        )
        .filter(
            RosterSwapRequest.to_person_id == member.person_id,
            RosterSwapRequest.status == "pending",
        )
        .order_by(RosterSwapRequest.requested_at.desc())
        .all()
    )
    return [RosterSwapResponse.model_validate(s) for s in swaps]
