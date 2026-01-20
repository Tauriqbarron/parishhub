"""API router for Mass Times management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.schemas.mass_times import MassTimeCreate, MassTimeResponse, MassTimeUpdate
from app.services.mass_times import MassTimeService

router = APIRouter(prefix="/api/mass-times", tags=["mass-times"])


def get_mass_time_service(db: Session = Depends(get_db)) -> MassTimeService:
    return MassTimeService(db)


@router.post(
    "",
    response_model=MassTimeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mass_time(
    data: MassTimeCreate,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MassTimeResponse:
    mass_time = service.create(data)
    return MassTimeResponse.model_validate(mass_time)


@router.get(
    "",
    response_model=list[MassTimeResponse],
)
async def list_mass_times(
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
    user: Annotated[User, Depends(require_auth)],
    active_only: Annotated[bool, Query()] = True,
) -> list[MassTimeResponse]:
    items = service.get_list(active_only=active_only)
    return [MassTimeResponse.model_validate(m) for m in items]


@router.get(
    "/{mass_time_id}",
    response_model=MassTimeResponse,
)
async def get_mass_time(
    mass_time_id: int,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MassTimeResponse:
    mass_time = service.get_by_id(mass_time_id)
    if not mass_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mass time not found",
        )
    return MassTimeResponse.model_validate(mass_time)


@router.put(
    "/{mass_time_id}",
    response_model=MassTimeResponse,
)
async def update_mass_time(
    mass_time_id: int,
    data: MassTimeUpdate,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MassTimeResponse:
    mass_time = service.update(mass_time_id, data)
    if not mass_time:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mass time not found",
        )
    return MassTimeResponse.model_validate(mass_time)


@router.delete(
    "/{mass_time_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_mass_time(
    mass_time_id: int,
    service: Annotated[MassTimeService, Depends(get_mass_time_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    deleted = service.delete(mass_time_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mass time not found",
        )
