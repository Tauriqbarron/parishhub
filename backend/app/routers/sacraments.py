"""API router for Sacrament CRUD operations."""

from datetime import date
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.models.sacrament import SacramentType
from app.schemas.pagination import PaginatedResponse
from app.schemas.sacrament import (
    SacramentCreate,
    SacramentResponse,
    SacramentUpdate,
)
from app.services.sacrament import SacramentService, SacramentValidationError

router = APIRouter(prefix="/api/sacraments", tags=["sacraments"])

# Secondary router for person-nested endpoints
persons_router = APIRouter(prefix="/api/persons", tags=["persons"])


def get_sacrament_service(db: Session = Depends(get_db)) -> SacramentService:
    """Dependency to get SacramentService instance."""
    return SacramentService(db)


@router.post(
    "",
    response_model=SacramentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new sacrament record",
)
async def create_sacrament(
    sacrament_data: SacramentCreate,
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> SacramentResponse:
    """
    Create a new sacrament record.

    Required fields:
    - person_id: ID of the person who received the sacrament
    - sacrament_type: Type of sacrament (baptism, first_communion, confirmation, marriage, holy_orders)
    - date_received: Date the sacrament was received

    Optional fields:
    - notes: Additional notes
    - additional_data: Type-specific data (godparents, sponsors, etc.)

    Validation:
    - Person cannot have duplicate sacrament types (except marriage)
    - First Communion must be after Baptism
    - Confirmation must be after First Communion
    """
    try:
        sacrament = service.create(sacrament_data)
        return SacramentResponse.model_validate(sacrament)
    except SacramentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    "",
    response_model=PaginatedResponse[SacramentResponse],
    summary="List all sacrament records",
)
async def list_sacraments(
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[
        int, Query(ge=1, le=100, description="Items per page")
    ] = 20,
    sacrament_type: Annotated[
        Optional[SacramentType], Query(description="Filter by sacrament type")
    ] = None,
    date_from: Annotated[
        Optional[date], Query(description="Filter by date received (from)")
    ] = None,
    date_to: Annotated[
        Optional[date], Query(description="Filter by date received (to)")
    ] = None,
    sort_by: Annotated[
        str,
        Query(
            description="Field to sort by",
            pattern="^(date_received|created_at|sacrament_type)$",
        ),
    ] = "date_received",
    sort_order: Annotated[
        str, Query(description="Sort order", pattern="^(asc|desc)$")
    ] = "desc",
) -> PaginatedResponse[SacramentResponse]:
    """
    List all sacrament records with pagination and filtering.

    Supports:
    - Pagination (page, per_page)
    - Filter by sacrament type
    - Filter by date range (date_from, date_to)
    - Sorting by date_received, created_at, or sacrament_type
    """
    items, total = service.get_list(
        page=page,
        per_page=per_page,
        sacrament_type=sacrament_type,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return PaginatedResponse.create(
        items=[SacramentResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/statistics",
    response_model=dict[str, Any],
    summary="Get sacrament statistics",
)
async def get_statistics(
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> dict[str, Any]:
    """
    Get sacrament statistics for dashboard.

    Returns:
    - Total counts for each sacrament type
    - Counts by year (last 5 years)
    """
    return service.get_statistics()


@router.get(
    "/{sacrament_id}",
    response_model=SacramentResponse,
    summary="Get a single sacrament record",
)
async def get_sacrament(
    sacrament_id: int,
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> SacramentResponse:
    """Get a single sacrament record by ID."""
    sacrament = service.get_by_id(sacrament_id)
    if not sacrament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacrament record not found",
        )
    return SacramentResponse.model_validate(sacrament)


@router.put(
    "/{sacrament_id}",
    response_model=SacramentResponse,
    summary="Update a sacrament record",
)
async def update_sacrament(
    sacrament_id: int,
    sacrament_data: SacramentUpdate,
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> SacramentResponse:
    """
    Update a sacrament record (partial update supported).

    Only fields provided in the request body will be updated.
    Note: person_id cannot be changed after creation.
    """
    try:
        sacrament = service.update(sacrament_id, sacrament_data)
        if not sacrament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sacrament record not found",
            )
        return SacramentResponse.model_validate(sacrament)
    except SacramentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.delete(
    "/{sacrament_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sacrament record",
)
async def delete_sacrament(
    sacrament_id: int,
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    """Delete a sacrament record."""
    deleted = service.delete(sacrament_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sacrament record not found",
        )


# Person-nested endpoints


@persons_router.post(
    "/{person_id}/sacraments",
    response_model=SacramentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a sacrament for a person",
    tags=["sacraments"],
)
async def create_person_sacrament(
    person_id: int,
    sacrament_data: SacramentCreate,
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> SacramentResponse:
    """
    Record a sacrament for a specific person.

    This is an alternative to POST /api/sacraments that automatically
    sets the person_id from the URL.
    """
    # Override person_id from URL
    sacrament_data_dict = sacrament_data.model_dump()
    sacrament_data_dict["person_id"] = person_id
    updated_data = SacramentCreate(**sacrament_data_dict)

    try:
        sacrament = service.create(updated_data)
        return SacramentResponse.model_validate(sacrament)
    except SacramentValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@persons_router.get(
    "/{person_id}/sacraments",
    response_model=list[SacramentResponse],
    summary="Get all sacraments for a person",
    tags=["sacraments"],
)
async def get_person_sacraments(
    person_id: int,
    service: Annotated[SacramentService, Depends(get_sacrament_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[SacramentResponse]:
    """Get all sacrament records for a specific person."""
    sacraments = service.get_by_person(person_id)
    return [SacramentResponse.model_validate(s) for s in sacraments]
