from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.sacrament import SacramentType


class SacramentBase(BaseModel):
    """Base schema for Sacrament with common fields."""

    person_id: int
    sacrament_type: SacramentType
    date_received: date
    notes: Optional[str] = None
    additional_data: Optional[dict[str, Any]] = None


class SacramentCreate(SacramentBase):
    """Schema for creating a new Sacrament."""

    pass


class SacramentUpdate(BaseModel):
    """Schema for updating an existing Sacrament. All fields optional."""

    sacrament_type: Optional[SacramentType] = None
    date_received: Optional[date] = None
    notes: Optional[str] = None
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

    godfather: Optional[str] = None
    godmother: Optional[str] = None
    minister: Optional[str] = None


class ConfirmationData(BaseModel):
    """Schema for confirmation-specific additional data."""

    sponsor: Optional[str] = None
    confirmation_name: Optional[str] = None
    bishop: Optional[str] = None


class MarriageData(BaseModel):
    """Schema for marriage-specific additional data."""

    spouse_id: Optional[int] = None
    spouse_name: Optional[str] = None
    witness1: Optional[str] = None
    witness2: Optional[str] = None
