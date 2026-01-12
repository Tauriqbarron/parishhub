"""API router for Household CRUD operations."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.models.household import HouseholdRole
from app.schemas.household import (
    HouseholdCreate,
    HouseholdMemberCreate,
    HouseholdMemberResponse,
    HouseholdMemberUpdate,
    HouseholdResponse,
    HouseholdUpdate,
    HouseholdWithMembers,
)
from app.schemas.pagination import PaginatedResponse
from app.services.household import HouseholdService

router = APIRouter(prefix="/api/households", tags=["households"])


def get_household_service(db: Session = Depends(get_db)) -> HouseholdService:
    """Dependency to get HouseholdService instance."""
    return HouseholdService(db)


class HouseholdCreateWithMembers(HouseholdCreate):
    """Schema for creating a household with optional initial members."""

    members: Optional[list[dict]] = None


@router.post(
    "",
    response_model=HouseholdWithMembers,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new household",
)
async def create_household(
    household_data: HouseholdCreateWithMembers,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
) -> HouseholdWithMembers:
    """
    Create a new household, optionally with initial members.

    Members should be provided as a list of objects with:
    - person_id: int (required)
    - role: str (head, spouse, child, other) (required)
    - is_primary_household: bool (optional, default True)
    """
    if household_data.members:
        # Validate member data
        for member in household_data.members:
            if "person_id" not in member or "role" not in member:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Each member must have person_id and role",
                )
            # Convert string role to enum
            try:
                member["role"] = HouseholdRole(member["role"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role: {member['role']}. Must be one of: head, spouse, child, other",
                )

        # Create household without members field
        create_data = HouseholdCreate(
            name=household_data.name,
            address_line1=household_data.address_line1,
            address_line2=household_data.address_line2,
            city=household_data.city,
            postal_code=household_data.postal_code,
        )
        household = service.create_with_members(create_data, household_data.members)
    else:
        create_data = HouseholdCreate(
            name=household_data.name,
            address_line1=household_data.address_line1,
            address_line2=household_data.address_line2,
            city=household_data.city,
            postal_code=household_data.postal_code,
        )
        household = service.create(create_data)

    # Reload with members
    household = service.get_by_id_with_members(household.id)
    return HouseholdWithMembers.model_validate(household)


@router.get(
    "",
    response_model=PaginatedResponse[HouseholdResponse],
    summary="List all households",
)
async def list_households(
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[
        int, Query(ge=1, le=100, description="Items per page")
    ] = 20,
    search: Annotated[
        Optional[str], Query(description="Search in household name")
    ] = None,
    sort_by: Annotated[
        str,
        Query(
            description="Field to sort by",
            pattern="^(name|created_at|updated_at)$",
        ),
    ] = "name",
    sort_order: Annotated[
        str, Query(description="Sort order", pattern="^(asc|desc)$")
    ] = "asc",
) -> PaginatedResponse[HouseholdResponse]:
    """
    List all households with pagination and filtering.

    Response includes member_count for each household.
    """
    items, total = service.get_list(
        page=page,
        per_page=per_page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return PaginatedResponse.create(
        items=[HouseholdResponse.model_validate(h) for h in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{household_id}",
    response_model=HouseholdWithMembers,
    summary="Get a single household",
)
async def get_household(
    household_id: int,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
) -> HouseholdWithMembers:
    """
    Get a single household by ID with full member details.
    """
    household = service.get_by_id_with_members(household_id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found",
        )
    return HouseholdWithMembers.model_validate(household)


@router.put(
    "/{household_id}",
    response_model=HouseholdResponse,
    summary="Update a household",
)
async def update_household(
    household_id: int,
    household_data: HouseholdUpdate,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
) -> HouseholdResponse:
    """
    Update a household (partial update supported).

    Only fields provided in the request body will be updated.
    """
    household = service.update(household_id, household_data)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found",
        )
    return HouseholdResponse.model_validate(household)


@router.delete(
    "/{household_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a household",
)
async def delete_household(
    household_id: int,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    """
    Delete a household.

    This will also remove all household memberships (cascade).
    """
    deleted = service.delete(household_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household not found",
        )


# Member operations


@router.post(
    "/{household_id}/members",
    response_model=HouseholdMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to a household",
)
async def add_household_member(
    household_id: int,
    person_id: int,
    role: HouseholdRole,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
    is_primary_household: bool = True,
) -> HouseholdMemberResponse:
    """
    Add a person to a household with a specified role.
    """
    member_data = HouseholdMemberCreate(
        household_id=household_id,
        person_id=person_id,
        role=role,
        is_primary_household=is_primary_household,
    )
    member = service.add_member(member_data)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add member. Household or person not found, or person is already a member.",
        )
    return HouseholdMemberResponse.model_validate(member)


@router.put(
    "/{household_id}/members/{person_id}",
    response_model=HouseholdMemberResponse,
    summary="Update a household member",
)
async def update_household_member(
    household_id: int,
    person_id: int,
    member_data: HouseholdMemberUpdate,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
) -> HouseholdMemberResponse:
    """
    Update a household member's role or primary status.
    """
    member = service.update_member(household_id, person_id, member_data)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household member not found",
        )
    return HouseholdMemberResponse.model_validate(member)


@router.delete(
    "/{household_id}/members/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a member from a household",
)
async def remove_household_member(
    household_id: int,
    person_id: int,
    service: Annotated[HouseholdService, Depends(get_household_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    """
    Remove a person from a household.
    """
    removed = service.remove_member(household_id, person_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household member not found",
        )
