"""Schemas for public registration endpoint."""

from datetime import date as Date
from typing import Optional

from pydantic import BaseModel, Field


class RegistrationMember(BaseModel):
    """A member in the registration submission."""

    # Accept both snake_case and camelCase for compatibility
    temp_id: str = Field(
        alias="tempId"
    )  # Frontend temporary ID for relationship mapping
    first_name: str = Field(min_length=1, max_length=100, alias="firstName")
    middle_name: Optional[str] = Field(default=None, max_length=100, alias="middleName")
    last_name: str = Field(min_length=1, max_length=100, alias="lastName")
    date_of_birth: Optional[Date] = Field(default=None, alias="dateOfBirth")
    gender: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = None
    is_head_of_household: bool = Field(default=False, alias="isHeadOfHousehold")
    lives_in_household: bool = Field(default=True, alias="livesInHousehold")

    model_config = {"populate_by_name": True}  # Allow both alias and field names


class RegistrationRelationship(BaseModel):
    """A relationship between two members in registration."""

    from_temp_id: str = Field(alias="fromTempId")
    to_temp_id: str = Field(alias="toTempId")
    relationship_type: str = Field(alias="relationshipType")

    model_config = {"populate_by_name": True}  # Allow both alias and field names


class RegistrationSacrament(BaseModel):
    """A sacrament record for a member in the registration."""

    member_temp_id: str = Field(alias="memberTempId")
    sacrament_type: str = Field(alias="sacramentType")
    date: Optional[Date] = None
    church: Optional[str] = None
    minister: Optional[str] = None
    # Typed sacrament-specific fields (replaced JSONB additionalData)
    godfather: Optional[str] = None
    godmother: Optional[str] = None
    sponsor: Optional[str] = None
    parish: Optional[str] = None
    witness1: Optional[str] = None
    witness2: Optional[str] = None
    officiant: Optional[str] = None
    notes: Optional[str] = None
    spouse_id: Optional[int] = Field(default=None, alias="spouseId")

    model_config = {"populate_by_name": True}  # Allow both alias and field names


class RegistrationConsent(BaseModel):
    """Consent data from registration form."""

    data_privacy_consent: bool = Field(alias="dataPrivacyConsent")
    photo_media_release: bool = Field(default=False, alias="photoMediaRelease")
    comm_email: bool = Field(default=False, alias="commEmail")
    comm_sms: bool = Field(default=False, alias="commSms")
    comm_phone: bool = Field(default=False, alias="commPhone")
    terms_acknowledged: bool = Field(alias="termsAcknowledged")

    model_config = {"populate_by_name": True}


class RegistrationSubmission(BaseModel):
    """Complete registration submission from public form."""

    household_name: str = Field(min_length=1, max_length=200)
    street_address: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20, alias="zipCode")
    country: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = None
    attending_since: Optional[Date] = Field(default=None, alias="attendingSince")
    members: list[RegistrationMember]
    relationships: list[RegistrationRelationship] = Field(default_factory=list)
    sacraments: list[RegistrationSacrament] = Field(default_factory=list)
    consent: Optional[RegistrationConsent] = None

    model_config = {"populate_by_name": True}  # Allow both alias and field names


class RegistrationResponse(BaseModel):
    """Response after successful registration."""

    household_id: int
    message: str = "Registration submitted successfully"


class IndividualRegistrationSubmission(BaseModel):
    """Registration submission for an individual (no household)."""

    first_name: str = Field(min_length=1, max_length=100, alias="firstName")
    middle_name: Optional[str] = Field(default=None, max_length=100, alias="middleName")
    last_name: str = Field(min_length=1, max_length=100, alias="lastName")
    date_of_birth: Optional[Date] = Field(default=None, alias="dateOfBirth")
    gender: Optional[str] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = None
    sacraments: list[RegistrationSacrament] = Field(default_factory=list)
    consent: Optional[RegistrationConsent] = None

    model_config = {"populate_by_name": True}


class IndividualRegistrationResponse(BaseModel):
    """Response after successful individual registration."""

    person_id: int
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
    registration_url: str = Field(description="Full URL for public registration page")
