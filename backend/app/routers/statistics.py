from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.models.household import Household
from app.models.person import Person
from app.models.sacrament import Sacrament, SacramentType

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


class DashboardStats(BaseModel):
    total_people: int
    total_households: int
    baptisms_this_year: int
    marriages_this_year: int


class RecentActivity(BaseModel):
    type: str
    description: str
    timestamp: datetime


class SacramentTrend(BaseModel):
    year: int
    baptism: int
    first_communion: int
    confirmation: int
    marriage: int
    holy_orders: int


class DashboardData(BaseModel):
    stats: DashboardStats
    recent_activity: list[RecentActivity]
    sacrament_trends: list[SacramentTrend]


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_statistics(
    user: Annotated[User, Depends(require_auth)],
    db: Session = Depends(get_db),
) -> DashboardData:
    """Get dashboard statistics including counts, recent activity, and trends."""
    current_year = datetime.now().year

    # Get total counts
    total_people = db.query(func.count(Person.id)).scalar() or 0
    total_households = db.query(func.count(Household.id)).scalar() or 0

    # Get sacraments for current year
    baptisms_this_year = (
        db.query(func.count(Sacrament.id))
        .filter(
            Sacrament.sacrament_type == SacramentType.BAPTISM,
            extract("year", Sacrament.date_received) == current_year,
        )
        .scalar()
        or 0
    )

    marriages_this_year = (
        db.query(func.count(Sacrament.id))
        .filter(
            Sacrament.sacrament_type == SacramentType.MARRIAGE,
            extract("year", Sacrament.date_received) == current_year,
        )
        .scalar()
        or 0
    )

    stats = DashboardStats(
        total_people=total_people,
        total_households=total_households,
        baptisms_this_year=baptisms_this_year,
        marriages_this_year=marriages_this_year,
    )

    # Get recent activity (last 10 items)
    recent_activity: list[RecentActivity] = []

    # Recent people added
    recent_people = (
        db.query(Person)
        .order_by(Person.created_at.desc())
        .limit(5)
        .all()
    )
    for person in recent_people:
        recent_activity.append(
            RecentActivity(
                type="person_added",
                description=f"{person.first_name} {person.last_name} added",
                timestamp=person.created_at,
            )
        )

    # Recent sacraments recorded
    recent_sacraments = (
        db.query(Sacrament)
        .order_by(Sacrament.created_at.desc())
        .limit(5)
        .all()
    )
    for sacrament in recent_sacraments:
        person = db.query(Person).filter(Person.id == sacrament.person_id).first()
        if person:
            sacrament_name = sacrament.sacrament_type.value.replace("_", " ").title()
            recent_activity.append(
                RecentActivity(
                    type="sacrament_recorded",
                    description=f"{person.first_name} {person.last_name} {sacrament_name} recorded",
                    timestamp=sacrament.created_at,
                )
            )

    # Recent households created
    recent_households = (
        db.query(Household)
        .order_by(Household.created_at.desc())
        .limit(5)
        .all()
    )
    for household in recent_households:
        recent_activity.append(
            RecentActivity(
                type="household_created",
                description=f"Household '{household.name}' created",
                timestamp=household.created_at,
            )
        )

    # Sort by timestamp and take top 10
    recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activity = recent_activity[:10]

    # Get sacrament trends for last 5 years
    sacrament_trends: list[SacramentTrend] = []
    for year in range(current_year - 4, current_year + 1):
        counts: dict[str, int] = {}
        for sacrament_type in SacramentType:
            count = (
                db.query(func.count(Sacrament.id))
                .filter(
                    Sacrament.sacrament_type == sacrament_type,
                    extract("year", Sacrament.date_received) == year,
                )
                .scalar()
                or 0
            )
            counts[sacrament_type.value] = count

        sacrament_trends.append(
            SacramentTrend(
                year=year,
                baptism=counts.get("baptism", 0),
                first_communion=counts.get("first_communion", 0),
                confirmation=counts.get("confirmation", 0),
                marriage=counts.get("marriage", 0),
                holy_orders=counts.get("holy_orders", 0),
            )
        )

    return DashboardData(
        stats=stats,
        recent_activity=recent_activity,
        sacrament_trends=sacrament_trends,
    )
