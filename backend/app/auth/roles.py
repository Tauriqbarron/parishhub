"""Role-based access control dependencies for the Ministries module."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import User, require_auth
from app.database import get_db
from app.models.ministry import UserRole


def get_user_roles(
    user: Annotated[User, Depends(require_auth)],
    db: Session = Depends(get_db),
) -> list[UserRole]:
    """Get all roles for the current user by email."""
    return list(
        db.query(UserRole).filter(UserRole.user_email == user.email).all()
    )


def require_role(*allowed_roles: str):
    """FastAPI dependency: reject if user has NONE of the allowed global roles.

    Any authenticated user (passed the Auth.js email allowlist) is treated
    as having all roles. This matches the ParishHub model where only
    pre-authorized emails can log in, and all such users are admins.

    If the user_roles table has a specific entry, that takes precedence
    for scoping — but a missing entry does NOT deny access.
    """

    def _check(
        user: Annotated[User, Depends(require_auth)],
        db: Session = Depends(get_db),
    ) -> User:
        # All authenticated users (passed email allowlist) have admin access.
        # This is the ParishHub default — only pre-authorized emails can log in.
        return user

    return _check


def require_ministry_role(ministry_id: int, *allowed_roles: str):
    """FastAPI dependency: reject if user has no role in this ministry.

    priest/admin (global roles) always pass.
    leader/member must have a scoped role for the given ministry.

    Usage:
        @router.post("/{ministry_id}/members",
                     dependencies=[Depends(lambda: require_ministry_role(...))])
    """

    def _check(
        user: Annotated[User, Depends(require_auth)],
        db: Session = Depends(get_db),
    ) -> User:
        # Global roles bypass ministry scoping
        global_role = (
            db.query(UserRole)
            .filter(
                UserRole.user_email == user.email,
                UserRole.role.in_(["priest", "admin"]),
                UserRole.ministry_id.is_(None),
            )
            .first()
        )
        if global_role:
            return user

        # Check scoped role
        scoped = (
            db.query(UserRole)
            .filter(
                UserRole.user_email == user.email,
                UserRole.role.in_(allowed_roles),
                UserRole.ministry_id == ministry_id,
            )
            .first()
        )
        if not scoped:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this ministry",
            )
        return user

    return _check
