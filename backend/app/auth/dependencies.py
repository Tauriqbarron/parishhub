"""Authentication dependencies for FastAPI routes."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.config import settings


class User(BaseModel):
    """Authenticated user model."""

    email: str
    name: str | None = None
    image: str | None = None


async def get_current_user(request: Request) -> User | None:
    """
    Extract user from X-User-Email header set by SvelteKit proxy.

    The SvelteKit server validates the Auth.js session and passes
    the authenticated user's email via a trusted header.
    """
    # Get user info from headers set by SvelteKit proxy
    email = request.headers.get("X-User-Email")
    name = request.headers.get("X-User-Name")

    if not email:
        return None

    # Verify this is the authorized email
    if email != settings.authorized_email:
        return None

    return User(
        email=email,
        name=name if name else None,
    )


async def require_auth(
    user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    """
    Dependency that requires authentication.
    Use this for protected routes.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
