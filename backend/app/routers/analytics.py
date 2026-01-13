"""API router for Analytics operations."""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.schemas.analytics import (
    AttendanceTrend,
    BirthCreate,
    BirthResponse,
    BirthStatistics,
    BirthUpdate,
    MassAttendanceCreate,
    MassAttendanceResponse,
    MassAttendanceUpdate,
    PopulationGrowth,
    PopulationSnapshotCreate,
    PopulationSnapshotResponse,
    PopulationSnapshotUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.services.analytics import BirthService, MassAttendanceService, PopulationService

# Births router
births_router = APIRouter(prefix="/api/births", tags=["births"])


def get_birth_service(db: Session = Depends(get_db)) -> BirthService:
    return BirthService(db)


@births_router.post(
    "",
    response_model=BirthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_birth(
    data: BirthCreate,
    service: Annotated[BirthService, Depends(get_birth_service)],
    user: Annotated[User, Depends(require_auth)],
) -> BirthResponse:
    birth = service.create(data)
    return BirthResponse.model_validate(birth)


@births_router.get(
    "",
    response_model=PaginatedResponse[BirthResponse],
)
async def list_births(
    service: Annotated[BirthService, Depends(get_birth_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    year: Annotated[Optional[int], Query()] = None,
) -> PaginatedResponse[BirthResponse]:
    items, total = service.get_list(page=page, per_page=per_page, year=year)
    return PaginatedResponse.create(
        items=[BirthResponse.model_validate(b) for b in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@births_router.get(
    "/statistics",
    response_model=BirthStatistics,
)
async def get_birth_statistics(
    service: Annotated[BirthService, Depends(get_birth_service)],
    user: Annotated[User, Depends(require_auth)],
    year: Annotated[Optional[int], Query()] = None,
) -> BirthStatistics:
    return service.get_birth_stats(year=year)


@births_router.get(
    "/{birth_id}",
    response_model=BirthResponse,
)
async def get_birth(
    birth_id: int,
    service: Annotated[BirthService, Depends(get_birth_service)],
    user: Annotated[User, Depends(require_auth)],
) -> BirthResponse:
    birth = service.get_by_id(birth_id)
    if not birth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth record not found",
        )
    return BirthResponse.model_validate(birth)


@births_router.put(
    "/{birth_id}",
    response_model=BirthResponse,
)
async def update_birth(
    birth_id: int,
    data: BirthUpdate,
    service: Annotated[BirthService, Depends(get_birth_service)],
    user: Annotated[User, Depends(require_auth)],
) -> BirthResponse:
    birth = service.update(birth_id, data)
    if not birth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth record not found",
        )
    return BirthResponse.model_validate(birth)


@births_router.delete(
    "/{birth_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_birth(
    birth_id: int,
    service: Annotated[BirthService, Depends(get_birth_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    deleted = service.delete(birth_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth record not found",
        )


# Mass Attendance router
attendance_router = APIRouter(prefix="/api/mass-attendance", tags=["mass-attendance"])


def get_attendance_service(db: Session = Depends(get_db)) -> MassAttendanceService:
    return MassAttendanceService(db)


@attendance_router.post(
    "",
    response_model=MassAttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_attendance(
    data: MassAttendanceCreate,
    service: Annotated[MassAttendanceService, Depends(get_attendance_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MassAttendanceResponse:
    attendance = service.create(data)
    return MassAttendanceResponse.model_validate(attendance)


@attendance_router.get(
    "",
    response_model=PaginatedResponse[MassAttendanceResponse],
)
async def list_attendance(
    service: Annotated[MassAttendanceService, Depends(get_attendance_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
    start_date: Annotated[Optional[date], Query()] = None,
    end_date: Annotated[Optional[date], Query()] = None,
) -> PaginatedResponse[MassAttendanceResponse]:
    items, total = service.get_list(
        page=page, per_page=per_page, start_date=start_date, end_date=end_date
    )
    return PaginatedResponse.create(
        items=[MassAttendanceResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@attendance_router.get(
    "/statistics",
    response_model=AttendanceTrend,
)
async def get_attendance_statistics(
    service: Annotated[MassAttendanceService, Depends(get_attendance_service)],
    user: Annotated[User, Depends(require_auth)],
) -> AttendanceTrend:
    return service.get_attendance_trends()


@attendance_router.get(
    "/{attendance_id}",
    response_model=MassAttendanceResponse,
)
async def get_attendance(
    attendance_id: int,
    service: Annotated[MassAttendanceService, Depends(get_attendance_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MassAttendanceResponse:
    attendance = service.get_by_id(attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found",
        )
    return MassAttendanceResponse.model_validate(attendance)


@attendance_router.put(
    "/{attendance_id}",
    response_model=MassAttendanceResponse,
)
async def update_attendance(
    attendance_id: int,
    data: MassAttendanceUpdate,
    service: Annotated[MassAttendanceService, Depends(get_attendance_service)],
    user: Annotated[User, Depends(require_auth)],
) -> MassAttendanceResponse:
    attendance = service.update(attendance_id, data)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found",
        )
    return MassAttendanceResponse.model_validate(attendance)


@attendance_router.delete(
    "/{attendance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attendance(
    attendance_id: int,
    service: Annotated[MassAttendanceService, Depends(get_attendance_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    deleted = service.delete(attendance_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found",
        )


# Population router
population_router = APIRouter(prefix="/api/population", tags=["population"])


def get_population_service(db: Session = Depends(get_db)) -> PopulationService:
    return PopulationService(db)


@population_router.post(
    "",
    response_model=PopulationSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_population_snapshot(
    data: PopulationSnapshotCreate,
    service: Annotated[PopulationService, Depends(get_population_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PopulationSnapshotResponse:
    snapshot = service.create(data)
    return PopulationSnapshotResponse.model_validate(snapshot)


@population_router.get(
    "",
    response_model=PaginatedResponse[PopulationSnapshotResponse],
)
async def list_population_snapshots(
    service: Annotated[PopulationService, Depends(get_population_service)],
    user: Annotated[User, Depends(require_auth)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[PopulationSnapshotResponse]:
    items, total = service.get_list(page=page, per_page=per_page)
    return PaginatedResponse.create(
        items=[PopulationSnapshotResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        per_page=per_page,
    )


@population_router.get(
    "/statistics",
    response_model=PopulationGrowth,
)
async def get_population_statistics(
    service: Annotated[PopulationService, Depends(get_population_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PopulationGrowth:
    return service.get_population_growth()


@population_router.get(
    "/{snapshot_id}",
    response_model=PopulationSnapshotResponse,
)
async def get_population_snapshot(
    snapshot_id: int,
    service: Annotated[PopulationService, Depends(get_population_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PopulationSnapshotResponse:
    snapshot = service.get_by_id(snapshot_id)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Population snapshot not found",
        )
    return PopulationSnapshotResponse.model_validate(snapshot)


@population_router.put(
    "/{snapshot_id}",
    response_model=PopulationSnapshotResponse,
)
async def update_population_snapshot(
    snapshot_id: int,
    data: PopulationSnapshotUpdate,
    service: Annotated[PopulationService, Depends(get_population_service)],
    user: Annotated[User, Depends(require_auth)],
) -> PopulationSnapshotResponse:
    snapshot = service.update(snapshot_id, data)
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Population snapshot not found",
        )
    return PopulationSnapshotResponse.model_validate(snapshot)


@population_router.delete(
    "/{snapshot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_population_snapshot(
    snapshot_id: int,
    service: Annotated[PopulationService, Depends(get_population_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    deleted = service.delete(snapshot_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Population snapshot not found",
        )
