"""API router for Roster admin CRUD operations."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.schemas.roster import (
    PersonRosterRoleCreate,
    PersonRosterRoleResponse,
    RosterAssignmentCreate,
    RosterAssignmentResponse,
    RosterAssignmentStatusUpdate,
    RosterInstanceResponse,
    RosterInstanceStatusUpdate,
    RosterRoleCreate,
    RosterRoleResponse,
    RosterRoleUpdate,
    RosterSwapCreate,
    RosterSwapResponse,
    RosterTemplateCreate,
    RosterTemplateResponse,
    RosterTemplateUpdate,
)
from app.services.roster import RosterService, RosterValidationError, get_roster_service

router = APIRouter(prefix="/api/roster", tags=["roster"])


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
@router.post(
    "/roles",
    response_model=RosterRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new roster role",
)
async def create_role(
    data: RosterRoleCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterRoleResponse:
    return RosterRoleResponse.model_validate(service.create_role(data))


@router.get(
    "/roles",
    response_model=list[RosterRoleResponse],
    summary="List all roster roles",
)
async def list_roles(
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[RosterRoleResponse]:
    roles = service.list_roles()
    return [RosterRoleResponse.model_validate(r) for r in roles]


@router.put(
    "/roles/{role_id}",
    response_model=RosterRoleResponse,
    summary="Update a roster role",
)
async def update_role(
    role_id: int,
    data: RosterRoleUpdate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterRoleResponse:
    try:
        role = service.update_role(role_id, data)
        return RosterRoleResponse.model_validate(role)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a roster role (fails if referenced by any slots)",
)
async def delete_role(
    role_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    try:
        service.delete_role(role_id)
    except RosterValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.message
        )


@router.post(
    "/roles/{role_id}/assign",
    response_model=PersonRosterRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a role to a person",
)
async def assign_role_to_person(
    role_id: int,
    data: PersonRosterRoleCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PersonRosterRoleResponse:
    try:
        prr = service.assign_role_to_person(data.person_id, role_id, None)  # Admin User has no id
        return PersonRosterRoleResponse.model_validate(prr)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete(
    "/roles/{role_id}/persons/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a role from a person",
)
async def remove_role_from_person(
    role_id: int,
    person_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    try:
        service.remove_role_from_person(person_id, role_id)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.get(
    "/persons/{person_id}/roles",
    response_model=list[RosterRoleResponse],
    summary="Get all roles for a person",
)
async def get_person_roles(
    person_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[RosterRoleResponse]:
    roles = service.get_person_roles(person_id)
    return [RosterRoleResponse.model_validate(r) for r in roles]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
@router.post(
    "/templates",
    response_model=RosterTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new roster template with slots",
)
async def create_template(
    data: RosterTemplateCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterTemplateResponse:
    template = service.create_template(data, created_by=None)  # Admin User has no id field
    return RosterTemplateResponse.model_validate(template)


@router.get(
    "/templates",
    response_model=list[RosterTemplateResponse],
    summary="List roster templates",
)
async def list_templates(
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
    ministry_id: Annotated[Optional[int], Query()] = None,
    is_active: Annotated[Optional[bool], Query()] = None,
) -> list[RosterTemplateResponse]:
    templates = service.list_templates(ministry_id, is_active)
    return [RosterTemplateResponse.model_validate(t) for t in templates]


@router.get(
    "/templates/{template_id}",
    response_model=RosterTemplateResponse,
    summary="Get a roster template with slots",
)
async def get_template(
    template_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterTemplateResponse:
    try:
        template = service.get_template(template_id)
        return RosterTemplateResponse.model_validate(template)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put(
    "/templates/{template_id}",
    response_model=RosterTemplateResponse,
    summary="Update a roster template",
)
async def update_template(
    template_id: int,
    data: RosterTemplateUpdate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterTemplateResponse:
    try:
        template = service.update_template(template_id, data)
        return RosterTemplateResponse.model_validate(template)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.delete(
    "/templates/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a roster template",
)
async def delete_template(
    template_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    try:
        service.delete_template(template_id)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post(
    "/templates/{template_id}/duplicate",
    response_model=RosterTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a roster template",
)
async def duplicate_template(
    template_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterTemplateResponse:
    try:
        template = service.duplicate_template(template_id)
        return RosterTemplateResponse.model_validate(template)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# ---------------------------------------------------------------------------
# Instances
# ---------------------------------------------------------------------------
@router.post(
    "/templates/{template_id}/generate",
    response_model=RosterInstanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a roster instance for a date",
)
async def generate_instance(
    template_id: int,
    date: Annotated[date, Query()],
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterInstanceResponse:
    try:
        instance = service.generate_instance(template_id, date)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.get(
    "/instances",
    response_model=list[RosterInstanceResponse],
    summary="List roster instances",
)
async def list_instances(
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
    date_from: Annotated[Optional[date], Query()] = None,
    date_to: Annotated[Optional[date], Query()] = None,
    ministry_id: Annotated[Optional[int], Query()] = None,
) -> list[RosterInstanceResponse]:
    instances = service.list_instances(date_from, date_to, ministry_id)
    return [RosterInstanceResponse.model_validate(i) for i in instances]


@router.get(
    "/instances/{instance_id}",
    response_model=RosterInstanceResponse,
    summary="Get a roster instance with assignments",
)
async def get_instance(
    instance_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterInstanceResponse:
    try:
        instance = service.get_instance(instance_id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.put(
    "/instances/{instance_id}/publish",
    response_model=RosterInstanceResponse,
    summary="Publish a roster instance",
)
async def publish_instance(
    instance_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterInstanceResponse:
    try:
        instance = service.publish_instance(instance_id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/instances/{instance_id}/cancel",
    response_model=RosterInstanceResponse,
    summary="Cancel a roster instance",
)
async def cancel_instance(
    instance_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterInstanceResponse:
    try:
        instance = service.cancel_instance(instance_id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.put(
    "/instances/{instance_id}/complete",
    response_model=RosterInstanceResponse,
    summary="Complete a roster instance",
)
async def complete_instance(
    instance_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterInstanceResponse:
    try:
        instance = service.complete_instance(instance_id)
        return RosterInstanceResponse.model_validate(instance)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


# ---------------------------------------------------------------------------
# Assignments (admin)
# ---------------------------------------------------------------------------
@router.post(
    "/instances/{instance_id}/assign",
    response_model=RosterAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a person to a roster slot",
)
async def assign_person(
    instance_id: int,
    data: RosterAssignmentCreate,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> RosterAssignmentResponse:
    try:
        assignment = service.assign_person(
            instance_id, data.slot_id, data.person_id, assigned_by=user.id
        )
        return RosterAssignmentResponse.model_validate(assignment)
    except RosterValidationError as e:
        if e.detail.get("missing_role"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=e.detail
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete(
    "/assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a roster assignment",
)
async def remove_assignment(
    assignment_id: int,
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    try:
        service.remove_assignment(assignment_id)
    except RosterValidationError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


# ---------------------------------------------------------------------------
# Parish Aggregate
# ---------------------------------------------------------------------------
@router.get(
    "/parish",
    summary="Get parish roster aggregate view for a date",
)
async def get_parish_aggregate(
    date: Annotated[date, Query()],
    service: Annotated[RosterService, Depends(get_roster_service)],
    user: Annotated[User, Depends(require_auth)],
):
    return service.get_parish_aggregate(date)
