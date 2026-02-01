from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.mass_times import MassTime
from app.schemas.mass_times import MassTimeCreate, MassTimeUpdate


class MassTimeService:
    """Service class for MassTime CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: MassTimeCreate) -> MassTime:
        mass_time = MassTime(**data.model_dump())
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

    def update(self, mass_time_id: int, data: MassTimeUpdate) -> Optional[MassTime]:
        mass_time = self.get_by_id(mass_time_id)
        if not mass_time:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mass_time, field, value)

        self.db.commit()
        self.db.refresh(mass_time)
        return mass_time

    def delete(self, mass_time_id: int) -> bool:
        mass_time = self.get_by_id(mass_time_id)
        if not mass_time:
            return False

        mass_time.is_active = False
        self.db.commit()
        return True
