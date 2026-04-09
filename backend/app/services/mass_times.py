from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.mass_times import MassTime
from app.repositories.mass_time import MassTimeRepository, SqlAlchemyMassTimeRepository
from app.schemas.mass_times import MassTimeCreate, MassTimeUpdate


class MassTimeService:
    """Service class for MassTime CRUD operations."""

    def __init__(self, repo: MassTimeRepository) -> None:
        self.repo = repo

    def create(self, data: MassTimeCreate) -> MassTime:
        mass_time = MassTime(**data.model_dump())
        return self.repo.create(mass_time)

    def get_by_id(self, mass_time_id: int) -> Optional[MassTime]:
        return self.repo.get_by_id(mass_time_id)

    def get_list(self, active_only: bool = True) -> list[MassTime]:
        return self.repo.get_list(active_only)

    def update(self, mass_time_id: int, data: MassTimeUpdate) -> Optional[MassTime]:
        mass_time = self.repo.get_by_id(mass_time_id)
        if not mass_time:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mass_time, field, value)

        self.repo.commit()
        self.repo.refresh(mass_time)
        return mass_time

    def delete(self, mass_time_id: int) -> bool:
        mass_time = self.repo.get_by_id(mass_time_id)
        if not mass_time:
            return False

        mass_time.is_active = False
        self.repo.commit()
        return True


def get_mass_time_service(db: Session = Depends(get_db)) -> MassTimeService:
    """Dependency to get MassTimeService instance."""
    return MassTimeService(SqlAlchemyMassTimeRepository(db))
