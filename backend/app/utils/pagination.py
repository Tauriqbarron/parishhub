"""Pagination utility for service layer."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select


def paginate(
    db: Session,
    stmt: Select,
    page: int = 1,
    per_page: int = 20,
    *,
    unique: bool = False,
) -> tuple[list, int]:
    """Apply pagination to a pre-filtered, pre-sorted SQLAlchemy select statement.

    Call this AFTER applying all .where() and .order_by() clauses to the statement.

    Args:
        db: SQLAlchemy session
        stmt: A prepared select statement (with filters and ordering applied)
        page: 1-indexed page number
        per_page: Items per page
        unique: If True, call .unique() on the result (needed for joinedload)

    Returns:
        Tuple of (items, total_count)
    """
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    offset = (page - 1) * per_page
    stmt = stmt.offset(offset).limit(per_page)

    result = db.execute(stmt)
    if unique:
        result = result.unique()
    items = list(result.scalars().all())
    return items, total
