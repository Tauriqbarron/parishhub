"""API router for Death operations."""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import User, require_auth
from app.schemas.death import (
    DeathCreate,
    DeathResponse,
    DeathStatistics,
    DeathUpdate,
    DeathWithPerson,
)
from app.schemas.pagination import PaginatedResponse
from app.services.death import DeathService, DeathValidationError, get_death_service

router = APIRouter(prefix="/api/deaths", tags=["deaths"])
persons_router = APIRouter(prefix="/api/persons", tags=["deaths"])


@router.post(
    "",
    response_model=DeathResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_death(
    data: DeathCreate,
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
) -> DeathResponse:
    try:
        death = service.create(data)
        return DeathResponse.model_validate(death)
    except DeathValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    "",
    response_model=PaginatedResponse[DeathWithPerson],
)
async def list_deaths(
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    year: Annotated[Optional[int], Query()] = None,
) -> PaginatedResponse[DeathWithPerson]:
    items, total = service.get_list(page=page, per_page=per_page, year=year)
    return PaginatedResponse.create(
        items=[DeathWithPerson.model_validate(d) for d in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get(
    "/statistics",
    response_model=DeathStatistics,
)
async def get_death_statistics(
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
    year: Annotated[Optional[int], Query()] = None,
) -> DeathStatistics:
    return service.get_statistics(year=year)


@router.get(
    "/{death_id}",
    response_model=DeathWithPerson,
)
async def get_death(
    death_id: int,
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
) -> DeathWithPerson:
    death = service.get_by_id(death_id)
    if not death:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Death record not found",
        )
    return DeathWithPerson.model_validate(death)


@router.put(
    "/{death_id}",
    response_model=DeathResponse,
)
async def update_death(
    death_id: int,
    data: DeathUpdate,
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
) -> DeathResponse:
    try:
        death = service.update(death_id, data)
        if not death:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Death record not found",
            )
        return DeathResponse.model_validate(death)
    except DeathValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.delete(
    "/{death_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_death(
    death_id: int,
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    deleted = service.delete(death_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Death record not found",
        )


# Person-specific endpoints
@persons_router.post(
    "/{person_id}/death",
    response_model=DeathResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_person_death(
    person_id: int,
    data: DeathCreate,
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
) -> DeathResponse:
    if person_id != data.person_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Person ID in URL does not match person ID in body",
        )
    try:
        death = service.create(data)
        return DeathResponse.model_validate(death)
    except DeathValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@persons_router.get(
    "/{person_id}/death",
    response_model=DeathWithPerson,
)
async def get_person_death(
    person_id: int,
    service: Annotated[DeathService, Depends(get_death_service)],
    user: Annotated[User, Depends(require_auth)],
) -> DeathWithPerson:
    death = service.get_by_person_id(person_id)
    if not death:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Death record not found for this person",
        )
    return DeathWithPerson.model_validate(death)
