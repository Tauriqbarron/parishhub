"""API router for Statistics endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.schemas.statistics import (
    DashboardData,
    DashboardStats,
    RecentActivity,
    SacramentTrend,
)
from app.services.statistics import StatisticsService

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


def get_statistics_service(db: Session = Depends(get_db)) -> StatisticsService:
    """Dependency to get StatisticsService instance."""
    return StatisticsService(db)


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_statistics(
    user: Annotated[User, Depends(require_auth)],
    service: Annotated[StatisticsService, Depends(get_statistics_service)],
) -> DashboardData:
    """Get dashboard statistics including counts, recent activity, and trends."""
    # Get basic stats
    stats_data = service.get_dashboard_stats()
    stats = DashboardStats(**stats_data)

    # Build recent activity list
    recent_activity: list[RecentActivity] = []

    # Recent people added
    for person in service.get_recent_people(5):
        recent_activity.append(
            RecentActivity(
                type="person_added",
                description=f"{person.first_name} {person.last_name} added",
                timestamp=person.created_at,
            )
        )

    # Recent sacraments recorded (with person data eager loaded)
    for sacrament in service.get_recent_sacraments_with_person(5):
        if sacrament.person:
            sacrament_name = sacrament.sacrament_type.value.replace("_", " ").title()
            recent_activity.append(
                RecentActivity(
                    type="sacrament_recorded",
                    description=f"{sacrament.person.first_name} {sacrament.person.last_name} {sacrament_name} recorded",
                    timestamp=sacrament.created_at,
                )
            )

    # Recent households created
    for household in service.get_recent_households(5):
        recent_activity.append(
            RecentActivity(
                type="household_created",
                description=f"Household '{household.name}' created",
                timestamp=household.created_at,
            )
        )

    # Recent deaths recorded
    from app.models.death import Death
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    recent_deaths_stmt = (
        select(Death)
        .options(selectinload(Death.person))
        .order_by(Death.created_at.desc())
        .limit(5)
    )
    recent_deaths = db.execute(recent_deaths_stmt).scalars().all()

    for death in recent_deaths:
        recent_activity.append(
            RecentActivity(
                type="death_recorded",
                description=f"{death.person.first_name} {death.person.last_name} death recorded",
                timestamp=death.created_at,
            )
        )

    # Sort by timestamp and take top 10
    recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activity = recent_activity[:10]

    # Get sacrament trends
    trends_data = service.get_sacrament_trends(5)
    sacrament_trends = [
        SacramentTrend(
            year=t["year"],
            baptism=t.get("baptism", 0),
            first_communion=t.get("first_communion", 0),
            confirmation=t.get("confirmation", 0),
            marriage=t.get("marriage", 0),
            holy_orders=t.get("holy_orders", 0),
        )
        for t in trends_data
    ]

    return DashboardData(
        stats=stats,
        recent_activity=recent_activity,
        sacrament_trends=sacrament_trends,
    )
