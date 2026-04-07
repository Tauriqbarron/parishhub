"""AuditService — logs every create/update/delete with user identity and timestamp.

OWASP/CIA compliance:
- Records full before/after state as JSON
- Associates actions with authenticated user email
- Provides queryable audit trail by resource, user, or time range
"""

from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    """Write and query the audit log."""

    def __init__(self, db: Session):
        self.db = db

    # -- Write operations --

    def log_create(
        self,
        resource_type: str,
        resource_id: int,
        new_values: dict[str, Any],
        user_email: str | None = None,
        user_ip: str | None = None,
        description: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_email=user_email,
            user_ip=user_ip,
            action="CREATE",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=None,
            new_values=new_values,
            description=description,
        )
        self.db.add(entry)
        return entry

    def log_update(
        self,
        resource_type: str,
        resource_id: int,
        old_values: dict[str, Any],
        new_values: dict[str, Any],
        user_email: str | None = None,
        user_ip: str | None = None,
        description: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_email=user_email,
            user_ip=user_ip,
            action="UPDATE",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
        )
        self.db.add(entry)
        return entry

    def log_delete(
        self,
        resource_type: str,
        resource_id: int,
        old_values: dict[str, Any],
        user_email: str | None = None,
        user_ip: str | None = None,
        description: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_email=user_email,
            user_ip=user_ip,
            action="DELETE",
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=None,
            description=description,
        )
        self.db.add(entry)
        return entry

    # -- Read operations --

    def get_by_resource(self, resource_type: str, resource_id: int) -> list[AuditLog]:
        """All audit entries for a specific resource instance."""
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
            .all()
        )

    def get_by_user(self, user_email: str) -> list[AuditLog]:
        """All audit entries performed by a specific user."""
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_email == user_email)
            .order_by(AuditLog.timestamp.desc())
            .all()
        )

    def get_recent(self, limit: int = 100) -> list[AuditLog]:
        """Most recent audit entries across all resources."""
        return (
            self.db.query(AuditLog)
            .order_by(AuditLog.timestamp.desc(), AuditLog.id.desc())
            .limit(limit)
            .all()
        )

    def get_by_date_range(self, start: date, end: date) -> list[AuditLog]:
        """Audit entries within a date range."""
        start_dt = datetime(start.year, start.month, start.day)
        end_dt = datetime(end.year, end.month, end.day, 23, 59, 59)
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.timestamp.between(start_dt, end_dt))
            .order_by(AuditLog.timestamp.desc())
            .all()
        )


def get_audit_service(db: Session = None) -> AuditService:
    """FastAPI dependency factory (placeholder — replaced in routes)."""
    if db is None:
        raise RuntimeError("AuditService requires a database session")
    return AuditService(db)
