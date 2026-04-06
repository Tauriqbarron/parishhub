"""Service layer for Person operations."""

from datetime import date
from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.household import HouseholdMember
from app.models.person import Person
from app.models.sacrament import Sacrament
from app.schemas.filters import PersonFilter
from app.schemas.person import PersonCreate, PersonUpdate
from app.utils.pagination import paginate


class PersonService:
    """Service class for Person CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, person_data: PersonCreate) -> Person:
        """Create a new person."""
        person = Person(**person_data.model_dump())
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def get_by_id(self, person_id: int) -> Optional[Person]:
        """Get a person by ID."""
        return self.db.get(Person, person_id)

    def get_by_id_with_relations(self, person_id: int) -> Optional[Person]:
        """Get a person by ID with all related data."""
        stmt = (
            select(Person)
            .options(
                selectinload(Person.household_memberships).selectinload(
                    HouseholdMember.household
                ),
                selectinload(Person.sacraments),
                selectinload(Person.relationships_as_person),
                selectinload(Person.relationships_as_related),
                selectinload(Person.death),
            )
            .where(Person.id == person_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_list(
        self,
        filters: PersonFilter,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "last_name",
        sort_order: str = "asc",
    ) -> tuple[list[Person], int]:
        """
        Get paginated list of persons with filtering and search.

        Returns tuple of (items, total_count).
        """
        stmt = select(Person).options(selectinload(Person.death))

        # Search filter
        if filters.search:
            search_term = f"%{filters.search}%"
            stmt = stmt.where(
                or_(
                    Person.first_name.ilike(search_term),
                    Person.last_name.ilike(search_term),
                    Person.email.ilike(search_term),
                )
            )

        # Gender filter
        if filters.gender:
            stmt = stmt.where(Person.gender == filters.gender)

        # Deceased filter
        if filters.is_deceased is not None:
            from app.models.death import Death

            if filters.is_deceased:
                stmt = stmt.where(Person.id.in_(select(Death.person_id)))
            else:
                stmt = stmt.where(Person.id.notin_(select(Death.person_id)))

        # Age filters
        today = date.today()
        if filters.min_age is not None:
            max_birth_date = date(today.year - filters.min_age, today.month, today.day)
            stmt = stmt.where(Person.date_of_birth <= max_birth_date)

        if filters.max_age is not None:
            min_birth_date = date(
                today.year - filters.max_age - 1, today.month, today.day
            )
            stmt = stmt.where(Person.date_of_birth > min_birth_date)

        # Sacrament filters
        if filters.has_sacrament:
            stmt = stmt.where(
                Person.id.in_(
                    select(Sacrament.person_id).where(
                        Sacrament.sacrament_type == filters.has_sacrament
                    )
                )
            )

        if filters.missing_sacrament:
            stmt = stmt.where(
                Person.id.notin_(
                    select(Sacrament.person_id).where(
                        Sacrament.sacrament_type == filters.missing_sacrament
                    )
                )
            )

        # Household filter
        if filters.has_household is not None:
            household_person_ids = select(HouseholdMember.person_id)
            if filters.has_household:
                stmt = stmt.where(Person.id.in_(household_person_ids))
            else:
                stmt = stmt.where(Person.id.notin_(household_person_ids))

        # Sorting
        sort_column = getattr(Person, sort_by, Person.last_name)
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()
        stmt = stmt.order_by(sort_column)

        # Get total count and apply pagination
        items, total = paginate(self.db, stmt, page, per_page)
        return items, total

    def update(self, person_id: int, person_data: PersonUpdate) -> Optional[Person]:
        """Update a person (partial update supported)."""
        person = self.get_by_id(person_id)
        if not person:
            return None

        update_data = person_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(person, field, value)

        self.db.commit()
        self.db.refresh(person)
        return person

    def delete(self, person_id: int, hard_delete: bool = False) -> bool:
        """
        Delete a person.

        Args:
            person_id: The ID of the person to delete
            hard_delete: If True, permanently delete. Otherwise, just return success.
                        (Soft delete could be implemented with an is_deleted field)

        Returns:
            True if deleted, False if not found.
        """
        person = self.get_by_id(person_id)
        if not person:
            return False

        self.db.delete(person)
        self.db.commit()
        return True

    def get_by_email(self, email: str) -> Optional[Person]:
        """Get a person by email address."""
        stmt = select(Person).where(Person.email == email)
        return self.db.execute(stmt).scalar_one_or_none()
