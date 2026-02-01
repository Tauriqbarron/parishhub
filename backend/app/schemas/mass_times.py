from datetime import datetime, time
from typing import Annotated, Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


def parse_time(v: Any) -> Optional[time]:
    if v is None:
        return None
    if isinstance(v, time):
        return v
    if isinstance(v, str):
        parts = v.split(":")
        if len(parts) == 2:
            return time(int(parts[0]), int(parts[1]))
        elif len(parts) == 3:
            return time(int(parts[0]), int(parts[1]), int(parts[2]))
    raise ValueError("Invalid time format")


class MassTimeBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    time: time
    day_of_week: Annotated[Optional[int], Field(ge=0, le=6)] = None
    is_active: bool = True

    @field_validator("time", mode="before")
    @classmethod
    def validate_time(cls, v: Any) -> time:
        result = parse_time(v)
        if result is None:
            raise ValueError("time is required")
        return result


class MassTimeCreate(MassTimeBase):
    pass


class MassTimeUpdate(BaseModel):
    name: Annotated[Optional[str], Field(min_length=1, max_length=100)] = None
    time: Any = None
    day_of_week: Annotated[Optional[int], Field(ge=0, le=6)] = None
    is_active: Optional[bool] = None

    @field_validator("time", mode="after")
    @classmethod
    def validate_time(cls, v: Any) -> Optional[time]:
        return parse_time(v)


class MassTimeResponse(MassTimeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
