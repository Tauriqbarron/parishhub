"""Authentication dependencies for FastAPI routes."""

import hmac
import hashlib
import time
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.config import settings


class User(BaseModel):
    """Authenticated user model."""

    email: str
    name: str | None = None
    image: str | None = None


def verify_signature(email: str, timestamp: str, signature: str) -> bool:
    """Verify the request signature using the shared secret."""
    if not settings.auth_secret:
        return False

    try:
        req_time = int(timestamp)
        current_time = int(time.time())
        # validate window of 5 minutes
        if abs(current_time - req_time) > 300:
            return False
    except ValueError:
        return False

    message = f"{timestamp}.{email}"
    expected_signature = hmac.new(
        settings.auth_secret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


async def get_current_user(request: Request) -> User | None:
    """
    Extract user from X-User-Email header set by SvelteKit proxy.
    Verifies HMAC signature to prevent header spoofing.
    """
    # Get user info from headers set by SvelteKit proxy
    email = request.headers.get("X-User-Email")
    name = request.headers.get("X-User-Name")
    timestamp = request.headers.get("X-Auth-Timestamp")
    signature = request.headers.get("X-Auth-Signature")

    if not email:
        return None

    if not timestamp or not signature:
        return None

    if not verify_signature(email, timestamp, signature):
        return None

    # Verify this is an authorized email
    if email not in settings.authorized_emails_list:
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
