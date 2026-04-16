"""Pydantic schemas for the Ministries module."""

from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Ministry
# ---------------------------------------------------------------------------
class MinistryBase(BaseModel):
    name: Annotated[str, Field(max_length=200)]
    description: Annotated[Optional[str], Field(max_length=5000)] = None
    leader_id: Optional[int] = None
    is_active: bool = True


class MinistryCreate(MinistryBase):
    pass


class MinistryUpdate(BaseModel):
    name: Annotated[Optional[str], Field(max_length=200)] = None
    description: Annotated[Optional[str], Field(max_length=5000)] = None
    leader_id: Optional[int] = None
    is_active: Optional[bool] = None


class MinistryResponse(MinistryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_count: int = 0
    created_at: datetime
    updated_at: datetime


class LeaderInfo(BaseModel):
    """Minimal person info for leader display."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: Optional[str] = None


class MinistryDetailResponse(MinistryResponse):
    members: list["MinistryMemberResponse"] = []
    events: list["MinistryEventResponse"] = []
    leader: Optional[LeaderInfo] = None


# ---------------------------------------------------------------------------
# MinistryMember
# ---------------------------------------------------------------------------
class MinistryMemberBase(BaseModel):
    ministry_id: int
    person_id: int
    role: Annotated[str, Field(max_length=50)] = "member"
    joined_date: Optional[date] = None
    is_active: bool = True


class MinistryMemberCreate(MinistryMemberBase):
    pass


class MinistryMemberUpdate(BaseModel):
    role: Annotated[Optional[str], Field(max_length=50)] = None
    is_active: Optional[bool] = None


class MinistryMemberResponse(MinistryMemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_name: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# MinistryEvent
# ---------------------------------------------------------------------------
class MinistryEventBase(BaseModel):
    ministry_id: int
    title: Annotated[str, Field(max_length=200)]
    description: Annotated[Optional[str], Field(max_length=5000)] = None
    event_date: date
    location: Annotated[Optional[str], Field(max_length=200)] = None


class MinistryEventCreate(MinistryEventBase):
    pass


class MinistryEventUpdate(BaseModel):
    title: Annotated[Optional[str], Field(max_length=200)] = None
    description: Annotated[Optional[str], Field(max_length=5000)] = None
    event_date: Optional[date] = None
    location: Annotated[Optional[str], Field(max_length=200)] = None


class MinistryEventResponse(MinistryEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attendance_count: int = 0
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
class AttendanceBatchCreate(BaseModel):
    person_ids: list[int]


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    person_id: int
    attended: bool
    person_name: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# UserRole
# ---------------------------------------------------------------------------
class UserRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_email: str
    role: str
    ministry_id: Optional[int] = None
    created_at: datetime
