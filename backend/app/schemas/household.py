from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.household import HouseholdRole


class HouseholdBase(BaseModel):
    """Base schema for Household with common fields."""

    name: str
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None


class HouseholdCreate(HouseholdBase):
    """Schema for creating a new Household."""

    pass


class HouseholdUpdate(BaseModel):
    """Schema for updating an existing Household. All fields optional."""

    name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None


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


class HouseholdWithMembers(HouseholdResponse):
    """Schema for Household with its members."""

    members: list[HouseholdMemberResponse] = []
