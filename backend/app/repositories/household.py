"""Repository protocols and implementations for Household entities."""

from typing import Optional, Protocol

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.household import Household, HouseholdMember
from app.models.person import Person
from app.utils.pagination import paginate


class HouseholdRepository(Protocol):
    """Protocol for Household data access."""

    def create(self, household: Household) -> Household: ...

    def flush(self) -> None: ...

    def refresh(self, obj) -> None: ...

    def get_by_id(self, household_id: int) -> Optional[Household]: ...

    def get_by_id_with_members(self, household_id: int) -> Optional[Household]: ...

    def get_list(
        self,
        stmt,
        page: int,
        per_page: int,
    ) -> tuple[list[Household], int]: ...

    def commit(self) -> None: ...

    def add(self, obj) -> None: ...

    def delete(self, obj) -> None: ...

    def get_member(
        self, household_id: int, person_id: int
    ) -> Optional[HouseholdMember]: ...

    def get_member_count(self, household_id: int) -> int: ...

    def person_exists(self, person_id: int) -> bool: ...
    def get_person(self, person_id: int) -> Optional[Person]: ...

    def update(self, obj) -> Household:
        """Commit and refresh a modified household object."""
        ...

    def update_member(self, obj) -> HouseholdMember:
        """Commit and refresh a modified household member object."""
        ...


class SqlAlchemyHouseholdRepository:
    """SQLAlchemy implementation of HouseholdRepository."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, household: Household) -> Household:
        self.db.add(household)
        self.db.commit()
        self.db.refresh(household)
        return household

    def flush(self) -> None:
        self.db.flush()

    def refresh(self, obj) -> None:
        self.db.refresh(obj)

    def get_by_id(self, household_id: int) -> Optional[Household]:
        return self.db.get(Household, household_id)

    def get_by_id_with_members(self, household_id: int) -> Optional[Household]:
        stmt = (
            select(Household)
            .options(
                selectinload(Household.members).selectinload(HouseholdMember.person)
            )
            .where(Household.id == household_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_list(
        self,
        stmt,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[Household], int]:
        return paginate(self.db, stmt, page, per_page)

    def commit(self) -> None:
        self.db.commit()

    def add(self, obj) -> None:
        self.db.add(obj)

    def delete(self, obj) -> None:
        self.db.delete(obj)

    def get_member(
        self, household_id: int, person_id: int
    ) -> Optional[HouseholdMember]:
        stmt = select(HouseholdMember).where(
            HouseholdMember.household_id == household_id,
            HouseholdMember.person_id == person_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_member_count(self, household_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(HouseholdMember)
            .where(HouseholdMember.household_id == household_id)
        )
        return self.db.execute(stmt).scalar() or 0

    def person_exists(self, person_id: int) -> bool:
        return self.db.get(Person, person_id) is not None

    def get_person(self, person_id: int) -> Optional[Person]:
        return self.db.get(Person, person_id)

    def update(self, obj) -> Household:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_member(self, obj) -> HouseholdMember:
        self.db.commit()
        self.db.refresh(obj)
        return obj
