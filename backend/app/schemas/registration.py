"""Schemas for public registration endpoint."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class RegistrationMember(BaseModel):
    """A member in the registration submission."""

    temp_id: str  # Frontend temporary ID for relationship mapping
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: Optional[str] = Field(default=None, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = None
    is_head_of_household: bool = False


class RegistrationRelationship(BaseModel):
    """A relationship between two members in the registration."""

    from_temp_id: str
    to_temp_id: str
    relationship_type: str


class RegistrationSacrament(BaseModel):
    """A sacrament record for a member in the registration."""

    member_temp_id: str
    sacrament_type: str
    date: Optional[date] = None
    church: Optional[str] = None
    minister: Optional[str] = None
    additional_data: dict = Field(default_factory=dict)


class RegistrationSubmission(BaseModel):
    """Complete registration submission from public form."""

    household_name: str = Field(min_length=1, max_length=200)
    street_address: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = None
    members: list[RegistrationMember]
    relationships: list[RegistrationRelationship] = Field(default_factory=list)
    sacraments: list[RegistrationSacrament] = Field(default_factory=list)


class RegistrationResponse(BaseModel):
    """Response after successful registration."""

    household_id: int
    message: str = "Registration submitted successfully"


class RegistrationURLConfig(BaseModel):
    """Configuration for registration URL base."""

    base_url: str = Field(
        min_length=1,
        description="Base URL for public registration (e.g., https://your-domain.com)",
    )


class RegistrationURLResponse(BaseModel):
    """Response with full registration URL."""

    base_url: str
    registration_url: str = Field(
        description="Full URL for public registration page"
    )
