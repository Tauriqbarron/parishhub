from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.household import Household
    from app.models.person import Person


class SacramentType(str, PyEnum):
    BAPTISM = "baptism"
    FIRST_COMMUNION = "first_communion"
    CONFIRMATION = "confirmation"
    MARRIAGE = "marriage"
    HOLY_ORDERS = "holy_orders"
    ANOINTING = "anointing"


class Sacrament(Base):
    """Records of sacraments received at this parish."""

    __tablename__ = "sacraments"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"), nullable=False
    )
    sacrament_type: Mapped[SacramentType] = mapped_column(
        Enum(SacramentType, name="sacrament_type_enum", create_constraint=True),
        nullable=False,
        index=True,
    )
    date_received: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Typed columns replacing the former JSONB additional_data column
    # (YAGNI: only store fields we actually use)
    godfather: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    godmother: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sponsor: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    minister: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    church: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parish: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    witness1: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    witness2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    officiant: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    spouse_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    person: Mapped["Person"] = relationship(
        "Person",
        foreign_keys=[person_id],
        back_populates="sacraments",
    )
    spouse: Mapped[Optional["Person"]] = relationship(
        "Person",
        foreign_keys=[spouse_id],
    )
    created_household: Mapped[Optional["Household"]] = relationship(
        "Household", back_populates="origin_sacrament"
    )

    def __repr__(self) -> str:
        return f"<Sacrament(id={self.id}, person_id={self.person_id}, type='{self.sacrament_type.value}')>"
