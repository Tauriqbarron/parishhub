"""Repository layer for Sacrament CRUD and queries (DIP compliant).

This module defines the abstract protocol (SacramentRepository) and a
SQLAlchemy implementation (SqlAlchemySacramentRepository).  The service
layer depends only on the protocol — not on SQLAlchemy — enabling easy
testing via fakes and clean architectural boundaries.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Optional

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.models.sacrament import Sacrament, SacramentType
from app.schemas.sacrament import SacramentCreate, SacramentUpdate


class SacramentRepository(ABC):
    """Abstract repository protocol for sacrament persistence operations.

    All database access for sacraments flows through this interface.
    Implementations hide the persistence mechanism (SQLAlchemy, mock, etc.)
    from the service layer, satisfying the Dependency Inversion Principle.
    """

    @abstractmethod
    def create(self, data: SacramentCreate) -> Sacrament:
        """Persist a new sacrament and return the committed instance."""
        ...

    @abstractmethod
    def get_by_id(self, sacrament_id: int) -> Optional[Sacrament]:
        """Fetch sacrament by primary key (no joins)."""
        ...

    @abstractmethod
    def get_by_id_with_person(self, sacrament_id: int) -> Optional[Sacrament]:
        """Fetch sacrament with person relationship eagerly loaded."""
        ...

    @abstractmethod
    def get_by_person(self, person_id: int) -> list[Sacrament]:
        """Return all sacraments for a person ordered by date received."""
        ...

    @abstractmethod
    def get_sacraments_by_person(
        self, person_id: int
    ) -> dict[SacramentType, Sacrament]:
        """Return sacraments for a person indexed by SacramentType."""
        ...

    @abstractmethod
    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        person_id: Optional[int] = None,
        sacrament_type: Optional[SacramentType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_by: str = "date_received",
        sort_order: str = "desc",
    ) -> tuple[list[Sacrament], int]:
        """Paginated, filterable sacrament listing.  Returns (items, total_count)."""
        ...

    @abstractmethod
    def update(self, sacrament_id: int, data: SacramentUpdate) -> Optional[Sacrament]:
        """Apply partial update and return the committed instance, or None if not found."""
        ...

    @abstractmethod
    def delete(self, sacrament_id: int) -> bool:
        """Delete the sacrament; return True if deleted, False if not found."""
        ...

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """Aggregate counts by type and by year (last 5 years) for dashboard."""
        ...


class SqlAlchemySacramentRepository(SacramentRepository):
    """SQLAlchemy implementation of SacramentRepository."""

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------------------------------
    # Helpers used internally by the repository
    # -----------------------------------------------------------------
    def _build_base_stmt(self):
        from sqlalchemy import select

        return select(Sacrament)

    def _apply_filters(
        self,
        stmt,
        person_id: Optional[int] = None,
        sacrament_type: Optional[SacramentType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
        if person_id is not None:
            stmt = stmt.where(Sacrament.person_id == person_id)
        if sacrament_type is not None:
            stmt = stmt.where(Sacrament.sacrament_type == sacrament_type)
        if date_from is not None:
            stmt = stmt.where(Sacrament.date_received >= date_from)
        if date_to is not None:
            stmt = stmt.where(Sacrament.date_received <= date_to)
        return stmt

    def _apply_sort(
        self, stmt, sort_by: str = "date_received", sort_order: str = "desc"
    ):
        column = getattr(Sacrament, sort_by, Sacrament.date_received)
        if sort_order.lower() == "desc":
            column = column.desc()
        return stmt.order_by(column)

    # -----------------------------------------------------------------
    # Public protocol methods
    # -----------------------------------------------------------------
    def create(self, data: SacramentCreate) -> Sacrament:
        dump = data.model_dump(exclude={"additional_data"})
        sacrament = Sacrament(**dump)
        self.db.add(sacrament)
        self.db.flush()
        self.db.commit()
        self.db.refresh(sacrament)
        return sacrament

    def get_by_id(self, sacrament_id: int) -> Optional[Sacrament]:
        return self.db.get(Sacrament, sacrament_id)

    def get_by_id_with_person(self, sacrament_id: int) -> Optional[Sacrament]:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        stmt = (
            select(Sacrament)
            .options(selectinload(Sacrament.person))
            .where(Sacrament.id == sacrament_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_person(self, person_id: int) -> list[Sacrament]:
        from sqlalchemy import select

        stmt = (
            select(Sacrament)
            .where(Sacrament.person_id == person_id)
            .order_by(Sacrament.date_received)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_sacraments_by_person(
        self, person_id: int
    ) -> dict[SacramentType, Sacrament]:
        sacraments = self.get_by_person(person_id)
        return {s.sacrament_type: s for s in sacraments}

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        person_id: Optional[int] = None,
        sacrament_type: Optional[SacramentType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_by: str = "date_received",
        sort_order: str = "desc",
    ) -> tuple[list[Sacrament], int]:
        stmt = self._build_base_stmt()
        stmt = self._apply_filters(stmt, person_id, sacrament_type, date_from, date_to)
        stmt = self._apply_sort(stmt, sort_by, sort_order)

        # Total count (before pagination)
        count_stmt = self._apply_filters(
            select(func.count()).select_from(Sacrament),
            person_id,
            sacrament_type,
            date_from,
            date_to,
        )
        total = self.db.execute(count_stmt).scalar() or 0

        # Pagination
        offset = (page - 1) * per_page
        items = list(
            self.db.execute(stmt.offset(offset).limit(per_page)).scalars().all()
        )

        return items, total

    def update(self, sacrament_id: int, data: SacramentUpdate) -> Optional[Sacrament]:
        sacrament = self.get_by_id(sacrament_id)
        if sacrament is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(sacrament, field, value)
        self.db.commit()
        self.db.refresh(sacrament)
        return sacrament

    def delete(self, sacrament_id: int) -> bool:
        sacrament = self.get_by_id(sacrament_id)
        if sacrament is None:
            return False
        self.db.delete(sacrament)
        self.db.commit()
        return True

    def get_statistics(self) -> dict[str, Any]:
        from datetime import date

        result: dict[str, Any] = {}

        # Counts by sacrament type
        for sacrament_type in SacramentType:
            stmt = select(func.count()).where(
                Sacrament.sacrament_type == sacrament_type
            )
            result[f"total_{sacrament_type.value}s"] = (
                self.db.execute(stmt).scalar() or 0
            )

        # Counts by year (last 5 years)
        by_year: dict[str, dict[str, int]] = {}
        current_year = date.today().year
        for year in range(current_year, current_year - 5, -1):
            year_counts: dict[str, int] = {}
            for sacrament_type in SacramentType:
                stmt = (
                    select(func.count())
                    .where(Sacrament.sacrament_type == sacrament_type)
                    .where(extract("year", Sacrament.date_received) == year)
                )
                year_counts[f"{sacrament_type.value}s"] = (
                    self.db.execute(stmt).scalar() or 0
                )
            by_year[str(year)] = year_counts

        result["by_year"] = by_year
        return result


class FakeSacramentRepository(SacramentRepository):
    """In-memory fake for unit tests."""

    def __init__(self):
        self._store: dict[int, Sacrament] = {}
        self._next_id = 1
        self.statistics_override: Optional[dict[str, Any]] = None

    def create(self, data: SacramentCreate) -> Sacrament:
        dump = data.model_dump(exclude={"additional_data"})
        sacrament = Sacrament(id=self._next_id, **dump)
        self._store[self._next_id] = sacrament
        self._next_id += 1
        return sacrament

    def get_by_id(self, sacrament_id: int) -> Optional[Sacrament]:
        return self._store.get(sacrament_id)

    def get_by_id_with_person(self, sacrament_id: int) -> Optional[Sacrament]:
        return self._store.get(sacrament_id)

    def get_by_person(self, person_id: int) -> list[Sacrament]:
        return [s for s in self._store.values() if s.person_id == person_id]

    def get_sacraments_by_person(
        self, person_id: int
    ) -> dict[SacramentType, Sacrament]:
        sacraments = self.get_by_person(person_id)
        return {s.sacrament_type: s for s in sacraments}

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        person_id: Optional[int] = None,
        sacrament_type: Optional[SacramentType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_by: str = "date_received",
        sort_order: str = "desc",
    ) -> tuple[list[Sacrament], int]:
        items = list(self._store.values())
        if person_id is not None:
            items = [s for s in items if s.person_id == person_id]
        if sacrament_type is not None:
            items = [s for s in items if s.sacrament_type == sacrament_type]
        if date_from is not None:
            items = [s for s in items if s.date_received >= date_from]
        if date_to is not None:
            items = [s for s in items if s.date_received <= date_to]
        total = len(items)
        items.sort(
            key=lambda s: getattr(s, sort_by, s.date_received),
            reverse=(sort_order == "desc"),
        )
        offset = (page - 1) * per_page
        return items[offset : offset + per_page], total

    def update(self, sacrament_id: int, data: SacramentUpdate) -> Optional[Sacrament]:
        sacrament = self._store.get(sacrament_id)
        if sacrament is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(sacrament, field, value)
        return sacrament

    def delete(self, sacrament_id: int) -> bool:
        if sacrament_id not in self._store:
            return False
        del self._store[sacrament_id]
        return True

    def get_statistics(self) -> dict[str, Any]:
        if self.statistics_override is not None:
            return self.statistics_override
        result: dict[str, Any] = {}
        all_sacraments = list(self._store.values())
        for sacrament_type in SacramentType:
            count = sum(1 for s in all_sacraments if s.sacrament_type == sacrament_type)
            result[f"total_{sacrament_type.value}s"] = count
        by_year: dict[str, dict[str, int]] = {}
        from datetime import date

        current_year = date.today().year
        for year in range(current_year, current_year - 5, -1):
            year_counts: dict[str, int] = {}
            for sacrament_type in SacramentType:
                count = sum(
                    1
                    for s in all_sacraments
                    if s.sacrament_type == sacrament_type
                    and s.date_received.year == year
                )
                year_counts[f"{sacrament_type.value}s"] = count
            by_year[str(year)] = year_counts
        result["by_year"] = by_year
        return result
