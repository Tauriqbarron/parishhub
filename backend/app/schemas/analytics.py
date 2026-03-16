import datetime as _dt
from datetime import date, datetime
from enum import Enum as PyEnum
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


class MetricType(str, PyEnum):
    BIRTH = "birth"
    MASS_ATTENDANCE = "mass_attendance"
    POPULATION = "population"


# ParishStatistic schemas
class ParishStatisticBase(BaseModel):
    metric_type: MetricType
    date: date
    value: int
    notes: Annotated[Optional[str], Field(max_length=2000)] = None
    additional_data: Optional[dict] = None


class ParishStatisticCreate(ParishStatisticBase):
    pass


class ParishStatisticUpdate(BaseModel):
    metric_type: Optional[MetricType] = None
    date: Optional[_dt.date] = None
    value: Optional[int] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None
    additional_data: Optional[dict] = None


class ParishStatisticResponse(ParishStatisticBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Birth schemas
class BirthBase(BaseModel):
    baby_first_name: Annotated[str, Field(min_length=1, max_length=100)]
    baby_last_name: Annotated[str, Field(min_length=1, max_length=100)]
    date_of_birth: date
    parent1_id: Optional[int] = None
    parent2_id: Optional[int] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None


class BirthCreate(BirthBase):
    pass


class BirthUpdate(BaseModel):
    baby_first_name: Annotated[Optional[str], Field(min_length=1, max_length=100)] = (
        None
    )
    baby_last_name: Annotated[Optional[str], Field(min_length=1, max_length=100)] = None
    date_of_birth: Optional[date] = None
    parent1_id: Optional[int] = None
    parent2_id: Optional[int] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None


class BirthResponse(BirthBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# MassAttendance schemas
class MassAttendanceBase(BaseModel):
    date: date
    mass_time: Annotated[Optional[str], Field(max_length=50)] = None
    attendance_count: Annotated[int, Field(ge=0)]
    notes: Annotated[Optional[str], Field(max_length=2000)] = None


class MassAttendanceCreate(MassAttendanceBase):
    mass_time_id: Optional[int] = None


class MassAttendanceUpdate(BaseModel):
    date: Optional[_dt.date] = None
    mass_time_id: Optional[int] = None
    mass_time: Annotated[Optional[str], Field(max_length=50)] = None
    attendance_count: Annotated[Optional[int], Field(ge=0)] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None


class MassAttendanceResponse(MassAttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mass_time_id: Optional[int] = None
    mass_time_name: Optional[str] = None
    mass_time_time: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# PopulationSnapshot schemas
class PopulationSnapshotBase(BaseModel):
    date: date
    registered_members: Annotated[int, Field(ge=0)]
    households: Annotated[int, Field(ge=0)]


class PopulationSnapshotCreate(PopulationSnapshotBase):
    pass


class PopulationSnapshotUpdate(BaseModel):
    date: Optional[_dt.date] = None
    registered_members: Annotated[Optional[int], Field(ge=0)] = None
    households: Annotated[Optional[int], Field(ge=0)] = None


class PopulationSnapshotResponse(PopulationSnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Statistics response schemas
class YearlyCount(BaseModel):
    year: int
    count: int


class BirthStatistics(BaseModel):
    by_year: list[YearlyCount]
    total: int
    current_year: int


class AttendanceTrend(BaseModel):
    weekly_average: float
    monthly_average: float
    yoy_change_percent: Optional[float] = None
    recent_weeks: list[dict]


class WeeklyDataPoint(BaseModel):
    date: str
    count: int


class MassTimeBreakdown(BaseModel):
    mass_time: str
    mass_time_id: Optional[int] = None
    total_attendance: int
    weekly_average: float
    recent_weeks: list[WeeklyDataPoint]


class AttendanceTrendExtended(AttendanceTrend):
    by_mass_time: list[MassTimeBreakdown]


class PopulationGrowth(BaseModel):
    history: list[PopulationSnapshotResponse]
    current_members: int
    current_households: int
    growth_percent: Optional[float] = None
