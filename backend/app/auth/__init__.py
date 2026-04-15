"""Authentication module for FastAPI."""

from app.auth.dependencies import User, get_current_user, require_auth
from app.auth.roles import get_user_roles, require_ministry_role, require_role

__all__ = [
    "User",
    "get_current_user",
    "require_auth",
    "get_user_roles",
    "require_role",
    "require_ministry_role",
]
