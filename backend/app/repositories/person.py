"""Repository protocol for Person domain.

Enables unit testing without a database and follows DIP (Dependency Inversion Principle).
"""

from typing import Optional, Protocol, runtime_checkable, Any
from sqlalchemy import select, func, Select
from sqlalchemy.orm import Session

from app.models.person import Person


@runtime_checkable
class PersonRepository(Protocol):
    """Abstract interface for person data access."""

    def get_by_id(self, person_id: int) -> Optional[Person]: ...
    def get_by_email(self, email: str) -> Optional[Person]: ...
    def get_by_id_with_relations(self, person_id: int) -> Optional[Person]: ...
    def save(self, person: Person) -> Person: ...
    def delete(self, person: Person) -> None: ...
    def list(self, stmt: Select[Any]) -> list[Person]: ...
    def count(self, stmt: Select[Any]) -> int: ...


class SqlAlchemyPersonRepository:
    """SQLAlchemy implementation of PersonRepository."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, person_id: int) -> Optional[Person]:
        return self.db.get(Person, person_id)

    def get_by_email(self, email: str) -> Optional[Person]:
        stmt = select(Person).where(Person.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id_with_relations(self, person_id: int) -> Optional[Person]:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        from app.models.household import HouseholdMember

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

    def save(self, person: Person) -> Person:
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def delete(self, person: Person) -> None:
        self.db.delete(person)
        self.db.commit()

    def list(self, stmt: Select[Any]) -> list[Person]:
        return list(self.db.execute(stmt).scalars().all())

    def count(self, stmt: Select[Any]) -> int:
        count_stmt = select(func.count()).select_from(stmt.subquery())
        return self.db.execute(count_stmt).scalar() or 0


class FakePersonRepository:
    """In-memory repository for unit testing PersonService without a DB."""

    def __init__(self, persons: list[Person] | None = None):
        self._persons: dict[int, Person] = {p.id: p for p in (persons or [])}
        self._next_id = max((p.id for p in self._persons.values()), default=0) + 1

    def get_by_id(self, person_id: int) -> Optional[Person]:
        return self._persons.get(person_id)

    def get_by_email(self, email: str) -> Optional[Person]:
        return next((p for p in self._persons.values() if p.email == email), None)

    def get_by_id_with_relations(self, person_id: int) -> Optional[Person]:
        return self._persons.get(person_id)

    def save(self, person: Person) -> Person:
        if person.id is None:
            person.id = self._next_id
            self._next_id += 1
        self._persons[person.id] = person
        return person

    def delete(self, person: Person) -> None:
        self._persons.pop(person.id, None)

    def list(self, stmt: Select[Any]) -> list[Person]:
        # Ignore stmt — return all persons (sufficient for unit tests)
        return list(self._persons.values())

    def count(self, stmt: Select[Any]) -> int:
        return len(self._persons)
