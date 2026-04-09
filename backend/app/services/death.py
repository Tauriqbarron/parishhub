"""Service layer for Death operations."""

from datetime import date
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.death import Death
from app.repositories.death import DeathRepository, SqlAlchemyDeathRepository
from app.schemas.death import (
    DeathCreate,
    DeathStatistics,
    DeathUpdate,
)


class DeathValidationError(Exception):
    """Exception raised for death validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DeathService:
    """Service class for Death CRUD and statistics operations."""

    def __init__(self, repo: DeathRepository, db: Session) -> None:
        self.repo = repo
        self.db = db

    def create(self, data: DeathCreate) -> Death:
        """Create a new death record with validation."""
        # 1. Check if person exists
        person = self.repo.get_person(data.person_id)
        if not person:
            raise DeathValidationError(f"Person with ID {data.person_id} not found")

        # 2. Check if person already has a death record
        existing_death = self.repo.get_by_person_id(data.person_id)
        if existing_death:
            raise DeathValidationError(
                f"Death record already exists for person ID {data.person_id}"
            )

        # 3. Check if date_of_death is in the future
        if data.date_of_death > date.today():
            raise DeathValidationError("Date of death cannot be in the future")

        # 4. Check if date_of_death is before birth date
        if data.date_of_birth and person.date_of_birth:
            if data.date_of_birth < person.date_of_birth:
                raise DeathValidationError(
                    f"Date of birth ({data.date_of_birth}) cannot be before date of birth ({person.date_of_birth})"
                )
        # Always use the person's actual DOB for death-before-birth check
        effective_dob = person.date_of_birth
        if effective_dob and data.date_of_death < effective_dob:
            raise DeathValidationError(
                f"Date of death ({data.date_of_death}) cannot be before date of birth ({effective_dob})"
            )

        # Create the death record (exclude date_of_birth - not a column)
        dump = data.model_dump(exclude={"date_of_birth"})
        death = Death(**dump)
        self.repo.add(death)
        self.repo.commit()
        self.repo.refresh(death)
        return death

    def get_by_id(self, death_id: int) -> Optional[Death]:
        """Get a single death record by its ID with person data."""
        return self.repo.get_by_id(death_id)

    def get_by_person_id(self, person_id: int) -> Optional[Death]:
        """Get death record for a specific person."""
        return self.repo.get_by_person_id(person_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        year: Optional[int] = None,
    ) -> tuple[list[Death], int]:
        """Get a paginated list of death records."""
        return self.repo.get_list(page, per_page, year)

    def update(self, death_id: int, data: DeathUpdate) -> Optional[Death]:
        """Update an existing death record."""
        death = self.repo.get_by_id(death_id)
        if not death:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Validation for date updates
        if "date_of_death" in update_data:
            new_date = update_data["date_of_death"]
            if new_date > date.today():
                raise DeathValidationError("Date of death cannot be in the future")

            # Need to check against person's birth date
            person = self.repo.get_person(death.person_id)
            if person and person.date_of_birth and new_date < person.date_of_birth:
                raise DeathValidationError(
                    f"Date of death ({new_date}) cannot be before date of birth ({person.date_of_birth})"
                )

        for field, value in update_data.items():
            setattr(death, field, value)

        return self.repo.update(death)

    def delete(self, death_id: int) -> bool:
        """Delete a death record."""
        death = self.repo.get_by_id(death_id)
        if not death:
            return False

        self.repo.delete(death)
        return True

    def get_statistics(self, year: Optional[int] = None) -> DeathStatistics:
        """Get death statistics."""
        return self.repo.get_statistics(year)


def get_death_service(db: Session = Depends(get_db)) -> DeathService:
    """Dependency to get DeathService instance."""
    return DeathService(SqlAlchemyDeathRepository(db), db)
