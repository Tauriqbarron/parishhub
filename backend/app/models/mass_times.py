from datetime import datetime, time as time_type
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MassTime(Base):
    """Configured mass time entity."""

    __tablename__ = "mass_times"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    time: Mapped[time_type] = mapped_column(Time, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    day_of_week: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
