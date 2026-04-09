"""Repository protocols and implementations for MassTime entities."""

from typing import Optional, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mass_times import MassTime


class MassTimeRepository(Protocol):
    """Protocol for MassTime data access."""

    def create(self, mass_time: MassTime) -> MassTime: ...

    def get_by_id(self, mass_time_id: int) -> Optional[MassTime]: ...

    def get_list(self, active_only: bool = True) -> list[MassTime]: ...

    def commit(self) -> None: ...

    def refresh(self, obj) -> None: ...


class SqlAlchemyMassTimeRepository:
    """SQLAlchemy implementation of MassTimeRepository."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, mass_time: MassTime) -> MassTime:
        self.db.add(mass_time)
        self.db.commit()
        self.db.refresh(mass_time)
        return mass_time

    def get_by_id(self, mass_time_id: int) -> Optional[MassTime]:
        return self.db.get(MassTime, mass_time_id)

    def get_list(self, active_only: bool = True) -> list[MassTime]:
        stmt = select(MassTime)
        if active_only:
            stmt = stmt.where(MassTime.is_active.is_(True))
        stmt = stmt.order_by(MassTime.time)
        return list(self.db.execute(stmt).scalars().all())

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, obj) -> None:
        self.db.refresh(obj)
