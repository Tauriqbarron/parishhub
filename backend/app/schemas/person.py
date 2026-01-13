import re
from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.person import Gender

PHONE_REGEX = re.compile(r"^\+?[\d\s\-().]{7,20}$")


class PersonBase(BaseModel):
    """Base schema for Person with common fields."""

    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    middle_name: Annotated[Optional[str], Field(max_length=100)] = None
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Annotated[Optional[str], Field(max_length=20)] = None
    address_line1: Annotated[Optional[str], Field(max_length=255)] = None
    address_line2: Annotated[Optional[str], Field(max_length=255)] = None
    city: Annotated[Optional[str], Field(max_length=100)] = None
    postal_code: Annotated[Optional[str], Field(max_length=20)] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone number format")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class PersonCreate(PersonBase):
    """Schema for creating a new Person."""

    pass


class PersonUpdate(BaseModel):
    """Schema for updating an existing Person. All fields optional."""

    first_name: Annotated[Optional[str], Field(min_length=1, max_length=100)] = None
    middle_name: Annotated[Optional[str], Field(max_length=100)] = None
    last_name: Annotated[Optional[str], Field(min_length=1, max_length=100)] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Annotated[Optional[str], Field(max_length=20)] = None
    address_line1: Annotated[Optional[str], Field(max_length=255)] = None
    address_line2: Annotated[Optional[str], Field(max_length=255)] = None
    city: Annotated[Optional[str], Field(max_length=100)] = None
    postal_code: Annotated[Optional[str], Field(max_length=20)] = None
    notes: Annotated[Optional[str], Field(max_length=2000)] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not PHONE_REGEX.match(v):
            raise ValueError("Invalid phone number format")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


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
