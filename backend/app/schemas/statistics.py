"""Schemas for statistics endpoints."""

from datetime import datetime

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Basic dashboard statistics."""

    total_people: int
    total_households: int
    baptisms_this_year: int
    marriages_this_year: int
    deaths_this_year: int


class RecentActivity(BaseModel):
    """A recent activity item."""

    type: str
    description: str
    timestamp: datetime
    record_id: int | None = None
    record_type: str = "default"


class SacramentTrend(BaseModel):
    """Sacrament counts for a specific year."""

    year: int
    baptism: int
    first_communion: int
    confirmation: int
    marriage: int
    holy_orders: int
    anointing: int


class DashboardData(BaseModel):
    """Complete dashboard data response."""

    stats: DashboardStats
    recent_activity: list[RecentActivity]
    sacrament_trends: list[SacramentTrend]
