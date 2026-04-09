"""Repository protocols and implementations for Death entities."""

from datetime import date
from typing import Optional, Protocol

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.death import Death
from app.models.person import Person
from app.schemas.death import DeathStatistics, YearlyDeathCount
from app.utils.pagination import paginate


class DeathRepository(Protocol):
    """Protocol for Death data access."""

    def create(self, death: Death) -> Death: ...

    def get_by_id(self, death_id: int) -> Optional[Death]: ...

    def get_by_person_id(self, person_id: int) -> Optional[Death]: ...

    def get_list(
        self, page: int, per_page: int, year: Optional[int]
    ) -> tuple[list[Death], int]: ...

    def update(self, death: Death) -> Death: ...

    def delete(self, death: Death) -> None: ...

    def get_statistics(self, year: Optional[int]) -> DeathStatistics: ...

    def get_person(self, person_id: int) -> Optional[Person]: ...

    def add(self, obj) -> None: ...

    def commit(self) -> None: ...

    def refresh(self, obj) -> None: ...


class SqlAlchemyDeathRepository:
    """SQLAlchemy implementation of DeathRepository."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, death: Death) -> Death:
        self.db.add(death)
        self.db.commit()
        self.db.refresh(death)
        return death

    def get_by_id(self, death_id: int) -> Optional[Death]:
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
        stmt = select(Death).options(
            selectinload(Death.person),
            selectinload(Death.officiating_priest),
        )

        if year:
            stmt = stmt.where(extract("year", Death.date_of_death) == year)

        stmt = stmt.order_by(Death.date_of_death.desc())
        return paginate(self.db, stmt, page, per_page)

    def update(self, death: Death) -> Death:
        self.db.commit()
        self.db.refresh(death)
        return death

    def delete(self, death: Death) -> None:
        self.db.delete(death)
        self.db.commit()

    def get_statistics(self, year: Optional[int] = None) -> DeathStatistics:
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

        current_year_stmt = select(func.count(Death.id)).where(
            extract("year", Death.date_of_death) == current_year
        )
        current_year_count = self.db.execute(current_year_stmt).scalar() or 0

        return DeathStatistics(
            by_year=by_year, total=total, current_year_count=current_year_count
        )

    def get_person(self, person_id: int) -> Optional[Person]:
        return self.db.get(Person, person_id)

    def add(self, obj) -> None:
        self.db.add(obj)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, obj) -> None:
        self.db.refresh(obj)
