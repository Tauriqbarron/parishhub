from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.mass_times import MassTime
    from app.models.person import Person


class MetricType(str, PyEnum):
    BIRTH = "birth"
    MASS_ATTENDANCE = "mass_attendance"
    POPULATION = "population"


class ParishStatistic(Base):
    """Generic parish statistic entity for flexible metrics."""

    __tablename__ = "parish_statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType, name="metric_type_enum", create_constraint=True),
        nullable=False,
        index=True,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ParishStatistic(id={self.id}, type={self.metric_type}, date={self.date})>"


class Birth(Base):
    """Birth record entity."""

    __tablename__ = "births"

    id: Mapped[int] = mapped_column(primary_key=True)
    baby_first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    baby_last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    parent1_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    parent2_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    parent1: Mapped[Optional["Person"]] = relationship(
        "Person", foreign_keys=[parent1_id]
    )
    parent2: Mapped[Optional["Person"]] = relationship(
        "Person", foreign_keys=[parent2_id]
    )

    def __repr__(self) -> str:
        return f"<Birth(id={self.id}, name='{self.baby_first_name} {self.baby_last_name}')>"


class MassAttendance(Base):
    """Mass attendance record entity."""

    __tablename__ = "mass_attendance"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    mass_time_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("mass_times.id", ondelete="SET NULL"), nullable=True, index=True
    )
    mass_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    attendance_count: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    mass_time_rel: Mapped[Optional["MassTime"]] = relationship("MassTime")

    @property
    def mass_time_name(self) -> Optional[str]:
        if self.mass_time_rel:
            return self.mass_time_rel.name
        return self.mass_time

    @property
    def mass_time_time(self) -> Optional[str]:
        if self.mass_time_rel:
            return self.mass_time_rel.time.strftime("%H:%M")
        return None

    def __repr__(self) -> str:
        return f"<MassAttendance(id={self.id}, date={self.date}, count={self.attendance_count})>"


class PopulationSnapshot(Base):
    """Population snapshot entity for tracking parish size over time."""

    __tablename__ = "population_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True, index=True)
    registered_members: Mapped[int] = mapped_column(Integer, nullable=False)
    households: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<PopulationSnapshot(id={self.id}, date={self.date}, members={self.registered_members})>"
