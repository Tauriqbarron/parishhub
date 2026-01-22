from datetime import date, datetime
from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.sacrament import SacramentType


class SacramentBase(BaseModel):
    """Base schema for Sacrament with common fields."""

    person_id: int
    sacrament_type: SacramentType
    date_received: date
    notes: Annotated[Optional[str], Field(max_length=2000)] = None
    additional_data: Optional[dict[str, Any]] = None


class SacramentCreate(SacramentBase):
    """Schema for creating a new Sacrament."""

    pass


class SacramentUpdate(BaseModel):
    """Schema for updating an existing Sacrament. All fields optional."""

    sacrament_type: Optional[SacramentType] = None
    date_received: Optional[date] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None
    additional_data: Optional[dict[str, Any]] = None


class SacramentResponse(SacramentBase):
    """Schema for Sacrament response including database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Additional data schemas for specific sacrament types
class BaptismData(BaseModel):
    """Schema for baptism-specific additional data."""

    godfather_id: Optional[int] = None
    godfather: Annotated[Optional[str], Field(max_length=200)] = None
    godmother_id: Optional[int] = None
    godmother: Annotated[Optional[str], Field(max_length=200)] = None
    minister_id: Optional[int] = None
    minister: Annotated[Optional[str], Field(max_length=200)] = None


class ConfirmationData(BaseModel):
    """Schema for confirmation-specific additional data."""

    sponsor_id: Optional[int] = None
    sponsor: Annotated[Optional[str], Field(max_length=200)] = None
    confirmation_name: Annotated[Optional[str], Field(max_length=100)] = None
    bishop_id: Optional[int] = None
    bishop: Annotated[Optional[str], Field(max_length=200)] = None


class MarriageData(BaseModel):
    """Schema for marriage-specific additional data."""

    spouse_id: Optional[int] = None
    spouse_name: Annotated[Optional[str], Field(max_length=200)] = None
    witness1_id: Optional[int] = None
    witness1: Annotated[Optional[str], Field(max_length=200)] = None
    witness2_id: Optional[int] = None
    witness2: Annotated[Optional[str], Field(max_length=200)] = None
