from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeathBase(BaseModel):
    """Base schema for Death with common fields."""

    person_id: int
    date_of_death: date
    place_of_death: Annotated[Optional[str], Field(max_length=255)] = None
    cause_of_death: Annotated[Optional[str], Field(max_length=255)] = None
    burial_date: Optional[date] = None
    burial_location: Annotated[Optional[str], Field(max_length=255)] = None
    funeral_date: Optional[date] = None
    funeral_location: Annotated[Optional[str], Field(max_length=255)] = None
    officiating_priest_id: Optional[int] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None

    @field_validator("date_of_death")
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of death cannot be in the future")
        return v


class DeathCreate(DeathBase):
    """Schema for creating a new Death record."""

    pass


class DeathUpdate(BaseModel):
    """Schema for updating an existing Death record."""

    date_of_death: Optional[date] = None
    place_of_death: Annotated[Optional[str], Field(max_length=255)] = None
    cause_of_death: Annotated[Optional[str], Field(max_length=255)] = None
    burial_date: Optional[date] = None
    burial_location: Annotated[Optional[str], Field(max_length=255)] = None
    funeral_date: Optional[date] = None
    funeral_location: Annotated[Optional[str], Field(max_length=255)] = None
    officiating_priest_id: Optional[int] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None

    @field_validator("date_of_death")
    @classmethod
    def validate_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Date of death cannot be in the future")
        return v


class DeathResponse(DeathBase):
    """Schema for Death response including database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class DeathPersonMinimal(BaseModel):
    """Minimal person representation for nested responses."""

    id: int
    first_name: str
    last_name: str

    model_config = ConfigDict(from_attributes=True)


class DeathWithPerson(DeathResponse):
    """Schema for Death with related person data."""

    person: DeathPersonMinimal
    officiating_priest: Optional[DeathPersonMinimal] = None


class YearlyDeathCount(BaseModel):
    """Helper for statistics."""

    year: int
    count: int


class DeathStatistics(BaseModel):
    """Schema for death statistics."""

    by_year: list[YearlyDeathCount]
    total: int
    current_year_count: int
