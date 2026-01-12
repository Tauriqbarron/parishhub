from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.person import Gender


class PersonBase(BaseModel):
    """Base schema for Person with common fields."""

    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    notes: Optional[str] = None


class PersonCreate(PersonBase):
    """Schema for creating a new Person."""

    pass


class PersonUpdate(BaseModel):
    """Schema for updating an existing Person. All fields optional."""

    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    notes: Optional[str] = None


class PersonResponse(PersonBase):
    """Schema for Person response including database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PersonWithRelations(PersonResponse):
    """Schema for Person with related data."""

    household_memberships: list["HouseholdMemberResponse"] = []
    sacraments: list["SacramentResponse"] = []


# Forward reference imports for type hints
from app.schemas.household import HouseholdMemberResponse  # noqa: E402
from app.schemas.sacrament import SacramentResponse  # noqa: E402

PersonWithRelations.model_rebuild()
