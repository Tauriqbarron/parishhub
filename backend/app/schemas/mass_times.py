from datetime import datetime, time
from typing import Annotated, Optional
from pydantic import BaseModel, ConfigDict, Field


class MassTimeBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    time: time
    day_of_week: Annotated[Optional[int], Field(ge=0, le=6)] = None
    is_active: bool = True


class MassTimeCreate(MassTimeBase):
    pass


class MassTimeUpdate(BaseModel):
    name: Annotated[Optional[str], Field(min_length=1, max_length=100)] = None
    time: Optional[time] = None
    day_of_week: Annotated[Optional[int], Field(ge=0, le=6)] = None
    is_active: Optional[bool] = None


class MassTimeResponse(MassTimeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
