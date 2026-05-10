"""Pydantic schemas for the Roster System."""

from datetime import date, datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# RosterRole
# ---------------------------------------------------------------------------
class RosterRoleBase(BaseModel):
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[Optional[str], Field(max_length=2000)] = None


class RosterRoleCreate(RosterRoleBase):
    pass


class RosterRoleUpdate(BaseModel):
    name: Annotated[Optional[str], Field(max_length=100)] = None
    description: Annotated[Optional[str], Field(max_length=2000)] = None


class RosterRoleResponse(RosterRoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    person_count: int = 0
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# PersonRosterRole
# ---------------------------------------------------------------------------
class PersonRosterRoleCreate(BaseModel):
    person_id: int
    role_id: int


class PersonRosterRoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    person_id: int
    role_id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# RosterTemplate
# ---------------------------------------------------------------------------
class RosterTemplateSettings(BaseModel):
    """Validated settings JSONB shape."""

    keep_assignee: bool = False
    auto_open_hours: int = Field(default=168, ge=1, le=720)  # 1 week default, max 30 days
    reminder_hours: list[int] = [48, 24]
    allow_self_assign: bool = True


class RosterTemplateBase(BaseModel):
    name: Annotated[str, Field(max_length=200)]
    description: Annotated[Optional[str], Field(max_length=5000)] = None
    ministry_id: Optional[int] = None
    mass_time_id: Optional[int] = None
    event_id: Optional[int] = None
    recurrence_rule: str = "none"  # none, weekly, biweekly, monthly
    recurrence_end: Optional[date] = None
    settings: RosterTemplateSettings = Field(default_factory=RosterTemplateSettings)
    is_active: bool = True


class RosterTemplateCreate(RosterTemplateBase):
    slots: list["RosterTemplateSlotCreate"] = []


class RosterTemplateUpdate(BaseModel):
    name: Annotated[Optional[str], Field(max_length=200)] = None
    description: Annotated[Optional[str], Field(max_length=5000)] = None
    ministry_id: Optional[int] = None
    mass_time_id: Optional[int] = None
    event_id: Optional[int] = None
    recurrence_rule: Optional[str] = None
    recurrence_end: Optional[date] = None
    settings: Optional[RosterTemplateSettings] = None
    is_active: Optional[bool] = None


class RosterTemplateResponse(RosterTemplateBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slots: list["RosterTemplateSlotResponse"] = []
    slot_count: int = 0
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# RosterTemplateSlot
# ---------------------------------------------------------------------------
class RosterTemplateSlotBase(BaseModel):
    role_id: int
    label: Annotated[str, Field(max_length=200)]
    sort_order: int = 0
    min_persons: int = 1
    max_persons: int = 1


class RosterTemplateSlotCreate(RosterTemplateSlotBase):
    pass


class RosterTemplateSlotUpdate(BaseModel):
    role_id: Optional[int] = None
    label: Annotated[Optional[str], Field(max_length=200)] = None
    sort_order: Optional[int] = None
    min_persons: Optional[int] = None
    max_persons: Optional[int] = None


class RosterTemplateSlotResponse(RosterTemplateSlotBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role_name: Optional[str] = None  # populated from relationship
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# RosterInstance
# ---------------------------------------------------------------------------
class RosterInstanceCreate(BaseModel):
    """Request schema for creating a roster instance from a template."""
    template_id: int
    date: date
    publish: bool = False  # If true, publish immediately
    notes: Optional[str] = None


class RosterInstanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    template_id: int
    template_name: Optional[str] = None
    date: date
    status: str
    generated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assignments: list["RosterAssignmentResponse"] = []
    created_at: datetime


class RosterInstanceStatusUpdate(BaseModel):
    status: str  # draft, published, completed, cancelled


# ---------------------------------------------------------------------------
# RosterAssignment
# ---------------------------------------------------------------------------
class RosterAssignmentCreate(BaseModel):
    instance_id: int
    slot_id: int
    person_id: int


class RosterAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    instance_id: int
    slot_id: int
    person_id: int
    person_name: Optional[str] = None  # populated from relationship
    slot_label: Optional[str] = None
    role_name: Optional[str] = None
    status: str
    assigned_by: Optional[int] = None
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    declined_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime


class RosterAssignmentStatusUpdate(BaseModel):
    status: str  # accepted, declined, completed, cancelled
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# RosterSwapRequest
# ---------------------------------------------------------------------------
class RosterSwapCreate(BaseModel):
    assignment_id: int
    to_person_id: int
    notes: Optional[str] = None


class RosterSwapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    assignment_id: int
    from_person_id: int
    from_person_name: Optional[str] = None
    to_person_id: int
    to_person_name: Optional[str] = None
    status: str
    requested_at: datetime
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
