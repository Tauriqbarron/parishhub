"""Service layer for Statistics operations."""

from datetime import datetime
from typing import Any

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.household import Household
from app.models.person import Person
from app.models.sacrament import Sacrament, SacramentType
from app.models.death import Death


class StatisticsService:
    """Service class for dashboard statistics operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_total_people(self) -> int:
        """Get total count of people."""
        stmt = select(func.count(Person.id))
        return self.db.execute(stmt).scalar() or 0

    def get_total_households(self) -> int:
        """Get total count of households."""
        stmt = select(func.count(Household.id))
        return self.db.execute(stmt).scalar() or 0

    def get_sacraments_by_type_and_year(
        self, sacrament_type: SacramentType, year: int
    ) -> int:
        """Get count of sacraments by type for a specific year."""
        stmt = select(func.count(Sacrament.id)).where(
            Sacrament.sacrament_type == sacrament_type,
            extract("year", Sacrament.date_received) == year,
        )
        return self.db.execute(stmt).scalar() or 0

    def get_deaths_by_year(self, year: int) -> int:
        """Get count of deaths for a specific year."""
        stmt = select(func.count(Death.id)).where(
            extract("year", Death.date_of_death) == year,
        )
        return self.db.execute(stmt).scalar() or 0

    def get_recent_people(self, limit: int = 5) -> list[Person]:
        """Get recently added people."""
        stmt = select(Person).order_by(Person.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_recent_sacraments_with_person(self, limit: int = 5) -> list[Sacrament]:
        """Get recently recorded sacraments with person data."""
        stmt = (
            select(Sacrament)
            .options(selectinload(Sacrament.person))
            .order_by(Sacrament.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_recent_households(self, limit: int = 5) -> list[Household]:
        """Get recently created households."""
        stmt = select(Household).order_by(Household.created_at.desc()).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_sacrament_trends(self, years: int = 5) -> list[dict[str, Any]]:
        """Get sacrament trends for the last N years."""
        current_year = datetime.now().year
        trends = []

        for year in range(current_year - years + 1, current_year + 1):
            year_data = {"year": year}
            for sacrament_type in SacramentType:
                count = self.get_sacraments_by_type_and_year(sacrament_type, year)
                year_data[sacrament_type.value] = count
            trends.append(year_data)

        return trends

    def get_dashboard_stats(self) -> dict[str, int]:
        """Get basic dashboard statistics."""
        current_year = datetime.now().year
        return {
            "total_people": self.get_total_people(),
            "total_households": self.get_total_households(),
            "baptisms_this_year": self.get_sacraments_by_type_and_year(
                SacramentType.BAPTISM, current_year
            ),
            "marriages_this_year": self.get_sacraments_by_type_and_year(
                SacramentType.MARRIAGE, current_year
            ),
            "deaths_this_year": self.get_deaths_by_year(current_year),
        }
