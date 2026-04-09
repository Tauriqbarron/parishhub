"""Service layer for Household operations."""

from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.household import Household, HouseholdMember
from app.repositories.household import (
    HouseholdRepository,
    SqlAlchemyHouseholdRepository,
)
from app.schemas.household import (
    HouseholdCreate,
    HouseholdMemberCreate,
    HouseholdMemberUpdate,
    HouseholdUpdate,
)


class HouseholdService:
    """Service class for Household CRUD operations."""

    def __init__(self, repo: HouseholdRepository, db: Session) -> None:
        self.repo = repo
        self.db = db

    def create(self, household_data: HouseholdCreate) -> Household:
        """Create a new household."""
        household = Household(**household_data.model_dump())
        return self.repo.create(household)

    def create_with_members(
        self,
        household_data: HouseholdCreate,
        members: list[dict],
    ) -> Household:
        """Create a new household with initial members."""
        household = Household(**household_data.model_dump())
        self.repo.add(household)
        self.repo.flush()  # Get the household ID

        for member_data in members:
            member = HouseholdMember(
                household_id=household.id,
                person_id=member_data["person_id"],
                role=member_data["role"],
                is_primary_household=member_data.get("is_primary_household", True),
            )
            self.repo.add(member)

        self.repo.commit()
        self.repo.refresh(household)
        return household

    def get_by_id(self, household_id: int) -> Optional[Household]:
        """Get a household by ID."""
        return self.repo.get_by_id(household_id)

    def get_by_id_with_members(self, household_id: int) -> Optional[Household]:
        """Get a household by ID with all members."""
        return self.repo.get_by_id_with_members(household_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Household], int]:
        """
        Get paginated list of households with filtering and search.

        Returns tuple of (items, total_count).
        """
        stmt = select(Household)

        # Search filter
        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(Household.name.ilike(search_term))

        # Sorting
        sort_column = getattr(Household, sort_by, Household.name)
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()
        stmt = stmt.order_by(sort_column)

        return self.repo.get_list(stmt, page, per_page)

    def update(
        self, household_id: int, household_data: HouseholdUpdate
    ) -> Optional[Household]:
        """Update a household (partial update supported)."""
        household = self.repo.get_by_id(household_id)
        if not household:
            return None

        update_data = household_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(household, field, value)

        return self.repo.update(household)

    def delete(self, household_id: int) -> bool:
        """Delete a household."""
        household = self.repo.get_by_id(household_id)
        if not household:
            return False

        self.repo.delete(household)
        self.repo.commit()
        return True

    # Member operations

    def add_member(
        self, member_data: HouseholdMemberCreate
    ) -> Optional[HouseholdMember]:
        """Add a person to a household."""
        # Verify household exists
        household = self.repo.get_by_id(member_data.household_id)
        if not household:
            return None

        # Verify person exists
        if not self.repo.person_exists(member_data.person_id):
            return None

        # Check if person is already a member
        existing = self.repo.get_member(member_data.household_id, member_data.person_id)
        if existing:
            return None

        member = HouseholdMember(**member_data.model_dump())
        self.repo.add(member)
        self.repo.commit()
        self.repo.refresh(member)
        return member

    def get_member(
        self, household_id: int, person_id: int
    ) -> Optional[HouseholdMember]:
        """Get a household member by household and person ID."""
        return self.repo.get_member(household_id, person_id)

    def update_member(
        self,
        household_id: int,
        person_id: int,
        member_data: HouseholdMemberUpdate,
    ) -> Optional[HouseholdMember]:
        """Update a household member's role or primary status."""
        member = self.repo.get_member(household_id, person_id)
        if not member:
            return None

        update_data = member_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(member, field, value)

        return self.repo.update_member(member)

    def remove_member(self, household_id: int, person_id: int) -> bool:
        """Remove a person from a household."""
        member = self.repo.get_member(household_id, person_id)
        if not member:
            return False

        self.repo.delete(member)
        return True

    def get_member_count(self, household_id: int) -> int:
        """Get the number of members in a household."""
        return self.repo.get_member_count(household_id)


def get_household_service(db: Session = Depends(get_db)) -> HouseholdService:
    """Dependency to get HouseholdService instance."""
    return HouseholdService(SqlAlchemyHouseholdRepository(db), db)
