"""API router for Person CRUD operations."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import User, require_auth
from app.models.person import Gender
from app.models.sacrament import SacramentType
from app.schemas.filters import PersonFilter
from app.schemas.pagination import PaginatedResponse
from app.schemas.person import (
    PersonCreate,
    PersonResponse,
    PersonUpdate,
    PersonWithRelations,
)
from app.services.person import PersonService, get_person_service

router = APIRouter(prefix="/api/persons", tags=["persons"])


@router.post(
    "",
    response_model=PersonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new person",
)
async def create_person(
    person_data: PersonCreate,
    service: Annotated[PersonService, Depends(get_person_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PersonResponse:
    """
    Create a new person with minimal required fields.

    Minimum required fields:
    - first_name
    - last_name

    All other fields are optional.
    """
    # Check for duplicate email if provided
    if person_data.email:
        existing = service.get_by_email(person_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A person with this email already exists",
            )

    person = service.create(person_data)
    return PersonResponse.model_validate(person)


@router.get(
    "",
    response_model=PaginatedResponse[PersonResponse],
    summary="List all persons",
)
async def list_persons(
    service: Annotated[PersonService, Depends(get_person_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    search: Annotated[
        Optional[str], Query(description="Search in first_name, last_name, email")
    ] = None,
    gender: Annotated[Optional[Gender], Query(description="Filter by gender")] = None,
    min_age: Annotated[
        Optional[int], Query(ge=0, description="Minimum age filter")
    ] = None,
    max_age: Annotated[
        Optional[int], Query(ge=0, description="Maximum age filter")
    ] = None,
    has_sacrament: Annotated[
        Optional[SacramentType], Query(description="Filter by sacrament received")
    ] = None,
    missing_sacrament: Annotated[
        Optional[SacramentType], Query(description="Filter by sacrament NOT received")
    ] = None,
    is_deceased: Annotated[
        Optional[bool], Query(description="Filter by deceased status")
    ] = None,
    has_household: Annotated[
        Optional[bool],
        Query(
            description="Filter by household membership (true=in household, false=individual)"
        ),
    ] = None,
    sort_by: Annotated[
        str,
        Query(
            description="Field to sort by",
            pattern="^(first_name|last_name|email|created_at|updated_at|date_of_birth)$",
        ),
    ] = "last_name",
    sort_order: Annotated[
        str, Query(description="Sort order", pattern="^(asc|desc)$")
    ] = "asc",
) -> PaginatedResponse[PersonResponse]:
    """
    List all persons with pagination and filtering.

    Supports:
    - Pagination (page, per_page)
    - Search across first_name, last_name, email
    - Filter by gender
    - Filter by age range (min_age, max_age)
    - Filter by sacrament received (has_sacrament)
    - Filter by sacrament NOT received (missing_sacrament)
    - Filter by deceased status (is_deceased)
    - Filter by household membership (has_household)
    - Sorting by various fields
    """
    filters = PersonFilter(
        search=search,
        gender=gender,
        min_age=min_age,
        max_age=max_age,
        has_sacrament=has_sacrament,
        missing_sacrament=missing_sacrament,
        is_deceased=is_deceased,
        has_household=has_household,
    )
    items, total = service.get_list(
        filters=filters,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return PaginatedResponse.create(
        items=[PersonResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/{person_id}",
    response_model=PersonWithRelations,
    summary="Get a single person",
)
async def get_person(
    person_id: int,
    service: Annotated[PersonService, Depends(get_person_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PersonWithRelations:
    """
    Get a single person by ID with all related data.

    Returns:
    - Basic person info
    - Household memberships
    - Sacraments received
    - Family relationships
    """
    person = service.get_by_id_with_relations(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return PersonWithRelations.model_validate(person)


@router.put(
    "/{person_id}",
    response_model=PersonResponse,
    summary="Update a person",
)
async def update_person(
    person_id: int,
    person_data: PersonUpdate,
    service: Annotated[PersonService, Depends(get_person_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PersonResponse:
    """
    Update a person (partial update supported).

    Only fields provided in the request body will be updated.
    """
    # Check for duplicate email if being updated
    if person_data.email:
        existing = service.get_by_email(person_data.email)
        if existing and existing.id != person_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A person with this email already exists",
            )

    person = service.update(person_id, person_data)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return PersonResponse.model_validate(person)


@router.delete(
    "/{person_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a person",
)
async def delete_person(
    person_id: int,
    service: Annotated[PersonService, Depends(get_person_service)],
    user: Annotated[User, Depends(require_auth)],
    hard_delete: Annotated[
        bool, Query(description="Permanently delete the person and related records")
    ] = True,
) -> None:
    """
    Delete a person.

    By default, performs a hard delete which removes the person and
    all related records (household memberships, sacraments, relationships)
    due to cascade settings.
    """
    deleted = service.delete(person_id, hard_delete=hard_delete)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
