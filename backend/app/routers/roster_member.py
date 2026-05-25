"""API router for member-facing roster operations."""

from datetime import date, datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.member import MemberUser, require_member
from app.schemas.roster import (
    PersonRosterRoleCreate,
    PersonRosterRoleResponse,
    RosterAssignmentCreate,
    RosterAssignmentResponse,
    RosterInstanceCreate,
    RosterInstanceResponse,
    RosterRoleCreate,
    RosterRoleResponse,
    RosterSwapCreate,
    RosterSwapResponse,
    RosterTemplateCreate,
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
# Roles (reference data)
# ---------------------------------------------------------------------------

@router.get(
    "/roles",
    response_model=list[RosterRoleResponse],
    summary="List all roster roles",
)
async def list_roles(
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> list[RosterRoleResponse]:
    """List all available roster roles (reference data)."""
    roles = service.list_roles()
    return [RosterRoleResponse.model_validate(r) for r in roles]


@router.post(
    "/roles",
    response_model=RosterRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new roster role (leader/admin only)",
)
async def create_role(
    data: RosterRoleCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterRoleResponse:
    """Create a new roster role. Any authenticated leader can create roles;
    they're shared reference data (not ministry-scoped)."""
    return RosterRoleResponse.model_validate(service.create_role(data))


# ---------------------------------------------------------------------------
# Person role assignment (leader only)
# ---------------------------------------------------------------------------

@router.post(
    "/roles/{role_id}/assign",
    response_model=PersonRosterRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a roster role to a person (leader only)",
)
async def assign_role_to_person(
    role_id: int,
    data: PersonRosterRoleCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> PersonRosterRoleResponse:
    """Assign a roster role to a person. Requires leader role."""
    if not any(r["role"] in ("leader", "admin", "co-leader") for r in member.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leaders can assign roles")
    try:
        prr = service.assign_role_to_person(data.person_id, role_id, assigned_by=member.person_id)
        return PersonRosterRoleResponse.model_validate(prr)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete(
    "/roles/{role_id}/persons/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a roster role from a person (leader only)",
)
async def remove_role_from_person(
    role_id: int,
    person_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
):
    """Remove a roster role from a person. Requires leader role."""
    if not any(r["role"] in ("leader", "admin", "co-leader") for r in member.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leaders can remove roles")
    try:
        service.remove_role_from_person(person_id, role_id)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/persons/{person_id}/roles",
    response_model=list[RosterRoleResponse],
    summary="Get roster roles assigned to a person",
)
async def get_person_roles(
    person_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> list[RosterRoleResponse]:
    """List roster roles assigned to a person."""
    roles = service.get_person_roles(person_id)
    return [RosterRoleResponse.model_validate(r) for r in roles]


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
# Parish Roster (visible to all members)
# ---------------------------------------------------------------------------

@router.get(
    "/parish",
    response_model=list[RosterInstanceResponse],
    summary="List all parish-wide roster instances",
)
async def list_parish_instances(
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
) -> list[RosterInstanceResponse]:
    """List roster instances from parish-wide templates (visible to all members)."""
    instances = service.list_parish_instances(date_from=date_from, date_to=date_to)
    return [RosterInstanceResponse.model_validate(i) for i in instances]


# ---------------------------------------------------------------------------
# Templates
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
# Leader assign person to slot
# ---------------------------------------------------------------------------

@router.post(
    "/instances/{instance_id}/assign",
    response_model=RosterAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a person to a roster slot (leader only)",
)
async def assign_person(
    instance_id: int,
    data: RosterAssignmentCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterAssignmentResponse:
    """Leader assigns a person to a roster slot."""
    if not any(r["role"] in ("leader", "admin", "co-leader") for r in member.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only leaders can assign people")
    try:
        assignment = service.assign_person(
            instance_id, data.slot_id, data.person_id, assigned_by=member.person_id
        )
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        if e.detail.get("missing_role"):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Person doesn't have the required roster role")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


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
        # Free the slot so others can take it
        assignment.person_id = None
        assignment.status = "pending"
        assignment.assigned_at = None
        assignment.accepted_at = None
        assignment.declined_at = datetime.now(timezone.utc)
        service.db.commit()
        service.db.refresh(assignment)
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
        if r["ministry_id"] == template.ministry_id and r["role"] in ("leader", "admin", "co-leader")
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
    include_parish: Annotated[bool, Query()] = True,
) -> list[RosterTemplateResponse]:
    """List active roster templates for a ministry. Member must belong to it.

    By default includes parish-wide templates. Set include_parish=false to
    get only templates scoped to this ministry (e.g. for instance creation).
    """
    member_ministry_ids = {r["ministry_id"] for r in member.roles if r.get("ministry_id")}
    if ministry_id not in member_ministry_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this ministry",
        )
    templates = service.list_templates(ministry_id=ministry_id, is_active=True, include_parish=include_parish)
    return [RosterTemplateResponse.model_validate(t) for t in templates]


@router.post(
    "/templates",
    response_model=RosterTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a roster template for a ministry (leader/admin only)",
)
async def create_template(
    data: RosterTemplateCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    member: Annotated[MemberUser, Depends(require_member)],
) -> RosterTemplateResponse:
    """Create a new roster template scoped to a ministry.

    Requires leader or admin role in the target ministry.
    """
    if not data.ministry_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ministry_id is required",
        )
    matching = [
        r for r in member.roles
        if r["ministry_id"] == data.ministry_id and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not matching:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be a leader or admin of this ministry to create templates",
        )
    try:
        template = service.create_template(data, created_by=member.person_id)
        return RosterTemplateResponse.model_validate(template)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


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
                if r["ministry_id"] == instance.template.ministry_id and r["role"] in ("leader", "admin", "co-leader")
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
