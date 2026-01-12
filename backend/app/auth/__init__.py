"""Authentication module for FastAPI."""

from app.auth.dependencies import User, get_current_user, require_auth

__all__ = ["User", "get_current_user", "require_auth"]
