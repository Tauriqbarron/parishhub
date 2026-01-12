"""Authentication dependencies for FastAPI routes."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import settings


class User(BaseModel):
    """Authenticated user model."""

    email: str
    name: str | None = None
    image: str | None = None


async def get_current_user(request: Request) -> User | None:
    """
    Extract and verify user from Auth.js session token.

    Auth.js stores session in a cookie named 'authjs.session-token'
    (or '__Secure-authjs.session-token' in production with HTTPS).
    """
    # Try both cookie names (secure and non-secure)
    token = request.cookies.get("authjs.session-token") or request.cookies.get(
        "__Secure-authjs.session-token"
    )

    if not token:
        return None

    if not settings.auth_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AUTH_SECRET not configured",
        )

    try:
        # Auth.js uses HS256 by default for JWT encoding
        payload = jwt.decode(
            token,
            settings.auth_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

        email: str | None = payload.get("email")
        if email is None:
            return None

        # Verify this is the authorized email
        if email != settings.authorized_email:
            return None

        return User(
            email=email,
            name=payload.get("name"),
            image=payload.get("picture"),
        )
    except JWTError:
        return None


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
