from datetime import date, datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.person import Person


class SacramentType(str, PyEnum):
    BAPTISM = "baptism"
    FIRST_COMMUNION = "first_communion"
    CONFIRMATION = "confirmation"
    MARRIAGE = "marriage"
    HOLY_ORDERS = "holy_orders"


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
    additional_data: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    person: Mapped["Person"] = relationship("Person", back_populates="sacraments")

    def __repr__(self) -> str:
        return f"<Sacrament(id={self.id}, person_id={self.person_id}, type='{self.sacrament_type.value}')>"
