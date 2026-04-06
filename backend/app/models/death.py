from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.person import Person


class Death(Base):
    """Records the death of a parishioner.

    Deletion semantics
    ------------------
    person_id (CASCADE):
        A Death record has no meaning without the Person it belongs to.
        When a Person row is deleted, their Death record is deleted
        automatically by the database.  This keeps referential integrity
        without requiring application-level cleanup.

    officiating_priest_id (SET NULL):
        The priest who officiated the funeral is a separate Person record.
        If that priest's record is ever deleted (e.g. a data-entry mistake),
        the Death record must be preserved — only the FK is cleared to NULL.
        The historical fact of the death is not affected by the priest's
        record being removed.
    """

    __tablename__ = "deaths"

    id: Mapped[int] = mapped_column(primary_key=True)

    # CASCADE: deleting the Person automatically removes their Death record.
    # A death record is existentially dependent on the person it describes.
    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One death record per person
        index=True,
    )

    date_of_death: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    place_of_death: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cause_of_death: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    burial_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    burial_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    funeral_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    funeral_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # SET NULL: if the officiating priest's Person record is deleted, we
    # preserve the Death record but lose the priest reference.  The
    # historical death event must not be erased just because a priest's
    # record is cleaned up.
    officiating_priest_id: Mapped[Optional[int]] = mapped_column(
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
    person: Mapped["Person"] = relationship(
        "Person", foreign_keys=[person_id], back_populates="death"
    )
    officiating_priest: Mapped[Optional["Person"]] = relationship(
        "Person", foreign_keys=[officiating_priest_id]
    )

    def __repr__(self) -> str:
        return f"<Death(id={self.id}, person_id={self.person_id}, date={self.date_of_death})>"
