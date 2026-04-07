"""API router for Mass Times management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import require_auth
from app.database import get_db
from app.schemas.mass_times import MassTimeCreate, MassTimeResponse, MassTimeUpdate
from app.services.mass_times import MassTimeService

# All routers — require authentication
router = APIRouter(
    prefix="/api/mass-times",
    tags=["mass-times"],
    dependencies=[Depends(require_auth)],
)

# Alias for admin routes (all routes are authenticated)
auth_router = router


def get_mass_time_service(db: Session = Depends(get_db)) -> MassTimeService:
    return MassTimeService(db)


# --- Public endpoints (parish website display) ---


@router.get(
    "",
    response_model=list[MassTimeResponse],
    summary="List mass times (public)",
)
async def list_mass_times(
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
    active_only: Annotated[bool, Query()] = True,
) -> list[MassTimeResponse]:
    items = service.get_list(active_only=active_only)
    return [MassTimeResponse.model_validate(m) for m in items]


@router.get(
    "/{mass_time_id}",
    response_model=MassTimeResponse,
    summary="Get mass time by ID (public)",
)
async def get_mass_time(
    mass_time_id: int,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
) -> MassTimeResponse:
    mass_time = service.get_by_id(mass_time_id)
    if not mass_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mass time not found",
        )
    return MassTimeResponse.model_validate(mass_time)


# --- Authenticated endpoints (admin operations) ---


@auth_router.post(
    "",
    response_model=MassTimeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create mass time (admin)",
)
async def create_mass_time(
    data: MassTimeCreate,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
) -> MassTimeResponse:
    mass_time = service.create(data)
    return MassTimeResponse.model_validate(mass_time)


@auth_router.put(
    "/{mass_time_id}",
    response_model=MassTimeResponse,
    summary="Update mass time (admin)",
)
async def update_mass_time(
    mass_time_id: int,
    data: MassTimeUpdate,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
) -> MassTimeResponse:
    mass_time = service.update(mass_time_id, data)
    if not mass_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mass time not found",
        )
    return MassTimeResponse.model_validate(mass_time)


@auth_router.delete(
    "/{mass_time_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete mass time (admin)",
)
async def delete_mass_time(
    mass_time_id: int,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
) -> None:
    deleted = service.delete(mass_time_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mass time not found",
        )
