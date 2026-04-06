"""Audit log model for tracking all data modifications.

OWASP/CIA compliance:
- Logs every create/update/delete with user identity, timestamp, and IP
- Immutable table — no UPDATE or DELETE operations allowed
- Captures old and new state as JSON for full audit trail
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Who performed the action
    user_email = Column(String(255), nullable=True, index=True)
    user_ip = Column(String(45), nullable=True)  # IPv6 max length

    # What was done
    action = Column(String(10), nullable=False, index=True)  # CREATE, UPDATE, DELETE
    resource_type = Column(
        String(50), nullable=False, index=True
    )  # e.g., "person", "sacrament", "death"
    resource_id = Column(Integer, nullable=False, index=True)

    # Data snapshot
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)

    # Context
    description = Column(Text, nullable=True)


__all__ = ["AuditLog"]
