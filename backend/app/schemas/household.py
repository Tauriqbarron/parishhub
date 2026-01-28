from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.household import HouseholdRole


class HouseholdBase(BaseModel):
    """Base schema for Household with common fields."""

    name: Annotated[str, Field(min_length=1, max_length=200)]
    address_line1: Annotated[Optional[str], Field(max_length=255)] = None
    address_line2: Annotated[Optional[str], Field(max_length=255)] = None
    city: Annotated[Optional[str], Field(max_length=100)] = None
    postal_code: Annotated[Optional[str], Field(max_length=20)] = None


class HouseholdCreate(HouseholdBase):
    """Schema for creating a new Household."""

    pass


class HouseholdUpdate(BaseModel):
    """Schema for updating an existing Household. All fields optional."""

    name: Annotated[Optional[str], Field(min_length=1, max_length=200)] = None
    address_line1: Annotated[Optional[str], Field(max_length=255)] = None
    address_line2: Annotated[Optional[str], Field(max_length=255)] = None
    city: Annotated[Optional[str], Field(max_length=100)] = None
    postal_code: Annotated[Optional[str], Field(max_length=20)] = None


class HouseholdResponse(HouseholdBase):
    """Schema for Household response including database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class HouseholdMemberBase(BaseModel):
    """Base schema for HouseholdMember."""

    household_id: int
    person_id: int
    role: HouseholdRole
    is_primary_household: bool = True


class HouseholdMemberCreate(HouseholdMemberBase):
    """Schema for creating a new HouseholdMember."""

    pass


class HouseholdMemberUpdate(BaseModel):
    """Schema for updating an existing HouseholdMember."""

    role: Optional[HouseholdRole] = None
    is_primary_household: Optional[bool] = None


class HouseholdMemberResponse(HouseholdMemberBase):
    """Schema for HouseholdMember response including database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    household: Optional["HouseholdResponse"] = None


class PersonSummary(BaseModel):
    """Brief person info for nested responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: Annotated[str, Field(max_length=100)]
    middle_name: Annotated[Optional[str], Field(max_length=100)] = None
    last_name: Annotated[str, Field(max_length=100)]


class HouseholdMemberWithPerson(HouseholdMemberResponse):
    """HouseholdMember response with person details."""

    person: Optional[PersonSummary] = None


class HouseholdWithMembers(HouseholdResponse):
    """Schema for Household with its members."""

    members: list[HouseholdMemberWithPerson] = []


class HouseholdCreateWithMembers(HouseholdCreate):
    """Schema for creating a household with optional initial members."""

    members: Optional[list[dict]] = None
