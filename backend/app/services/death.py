"""Service layer for Death operations."""

from datetime import date
from typing import Optional

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.death import Death
from app.models.person import Person
from app.schemas.death import (
    DeathCreate,
    DeathStatistics,
    DeathUpdate,
    YearlyDeathCount,
)


class DeathValidationError(Exception):
    """Exception raised for death validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class DeathService:
    """Service class for Death CRUD and statistics operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DeathCreate) -> Death:
        """Create a new death record with validation."""
        # 1. Check if person exists
        person = self.db.get(Person, data.person_id)
        if not person:
            raise DeathValidationError(f"Person with ID {data.person_id} not found")

        # 2. Check if person already has a death record
        existing_death = self.db.execute(
            select(Death).where(Death.person_id == data.person_id)
        ).scalar_one_or_none()
        if existing_death:
            raise DeathValidationError(f"Death record already exists for person ID {data.person_id}")

        # 3. Check if date_of_death is in the future
        if data.date_of_death > date.today():
            raise DeathValidationError("Date of death cannot be in the future")

        # 4. Check if date_of_death is after person's date_of_birth
        if person.date_of_birth and data.date_of_death < person.date_of_birth:
            raise DeathValidationError(
                f"Date of death ({data.date_of_death}) cannot be before date of birth ({person.date_of_birth})"
            )

        # Create the death record
        death = Death(**data.model_dump())
        self.db.add(death)
        self.db.commit()
        self.db.refresh(death)
        return death

    def get_by_id(self, death_id: int) -> Optional[Death]:
        """Get a single death record by its ID with person data."""
        stmt = (
            select(Death)
            .options(
                selectinload(Death.person),
                selectinload(Death.officiating_priest),
            )
            .where(Death.id == death_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_person_id(self, person_id: int) -> Optional[Death]:
        """Get death record for a specific person."""
        stmt = (
            select(Death)
            .options(
                selectinload(Death.person),
                selectinload(Death.officiating_priest),
            )
            .where(Death.person_id == person_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        year: Optional[int] = None,
    ) -> tuple[list[Death], int]:
        """Get a paginated list of death records."""
        stmt = select(Death).options(
            selectinload(Death.person),
            selectinload(Death.officiating_priest),
        )

        if year:
            stmt = stmt.where(extract("year", Death.date_of_death) == year)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = stmt.order_by(Death.date_of_death.desc())
        offset = (page - 1) * per_page
        stmt = stmt.offset(offset).limit(per_page)

        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def update(self, death_id: int, data: DeathUpdate) -> Optional[Death]:
        """Update an existing death record."""
        death = self.db.get(Death, death_id)
        if not death:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Validation for date updates
        if "date_of_death" in update_data:
            new_date = update_data["date_of_death"]
            if new_date > date.today():
                raise DeathValidationError("Date of death cannot be in the future")

            # Need to check against person's birth date
            person = self.db.get(Person, death.person_id)
            if person and person.date_of_birth and new_date < person.date_of_birth:
                raise DeathValidationError(
                    f"Date of death ({new_date}) cannot be before date of birth ({person.date_of_birth})"
                )

        for field, value in update_data.items():
            setattr(death, field, value)

        self.db.commit()
        self.db.refresh(death)
        return death

    def delete(self, death_id: int) -> bool:
        """Delete a death record."""
        death = self.db.get(Death, death_id)
        if not death:
            return False

        self.db.delete(death)
        self.db.commit()
        return True

    def get_statistics(self, year: Optional[int] = None) -> DeathStatistics:
        """Get death statistics."""
        current_year = date.today().year

        # Get yearly counts
        stmt = (
            select(
                extract("year", Death.date_of_death).label("year"),
                func.count(Death.id).label("count"),
            )
            .group_by(extract("year", Death.date_of_death))
            .order_by(extract("year", Death.date_of_death).desc())
        )

        if year:
            stmt = stmt.where(extract("year", Death.date_of_death) == year)

        results = self.db.execute(stmt).all()
        by_year = [YearlyDeathCount(year=int(r.year), count=r.count) for r in results]

        total_stmt = select(func.count(Death.id))
        if year:
            total_stmt = total_stmt.where(extract("year", Death.date_of_death) == year)
        total = self.db.execute(total_stmt).scalar() or 0

        # Current year count
        current_year_stmt = select(func.count(Death.id)).where(
            extract("year", Death.date_of_death) == current_year
        )
        current_year_count = self.db.execute(current_year_stmt).scalar() or 0

        return DeathStatistics(
            by_year=by_year, total=total, current_year_count=current_year_count
        )
