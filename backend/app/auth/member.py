"""JWT-based authentication for Ministries member frontend."""

import time
from typing import Annotated

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.config import settings

# JWT settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = 86400 * 7  # 7 days

# Google token verification URL
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"


class MemberUser(BaseModel):
    """Authenticated member (leader or regular member)."""

    email: str
    name: str | None = None
    picture: str | None = None
    person_id: int | None = None
    roles: list[dict] = []  # [{"role": "leader", "ministry_id": 1}, ...]


def create_member_token(email: str, name: str | None, picture: str | None) -> str:
    """Create a JWT token for a member."""
    payload = {
        "sub": email,
        "name": name,
        "picture": picture,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRY_SECONDS,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=JWT_ALGORITHM)


def decode_member_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def verify_google_token(id_token: str) -> dict:
    """Verify a Google ID token and return user info."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            GOOGLE_TOKEN_INFO_URL,
            params={"id_token": id_token},
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
            )
        data = resp.json()

        # Verify the token was issued for our app
        aud = data.get("aud", "")
        if settings.google_client_id and aud != settings.google_client_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token was not issued for this application",
            )

        return {
            "email": data.get("email"),
            "name": data.get("name"),
            "picture": data.get("picture"),
            "email_verified": data.get("email_verified", False),
        }


async def get_member_from_token(token: str, db) -> MemberUser:
    """Decode JWT, look up roles and person_id from DB, return MemberUser."""
    payload = decode_member_token(token)
    email = payload["sub"]

    from app.models.ministry import MinistryMember, UserRole
    from app.models.person import Person

    # Get user's Person record
    person = db.query(Person).filter(Person.email == email).first()
    person_id = person.id if person else None

    # Get user's roles
    roles_query = db.query(UserRole).filter(UserRole.user_email == email).all()
    roles = [{"role": r.role, "ministry_id": r.ministry_id} for r in roles_query]

    # Also check ministry_members for member-level access
    memberships = (
        db.query(MinistryMember)
        .filter(MinistryMember.person.has(email=email))
        .all()
    )
    for m in memberships:
        role_entry = {"role": m.role, "ministry_id": m.ministry_id}
        if role_entry not in roles:
            roles.append(role_entry)

    return MemberUser(
        email=email,
        name=payload.get("name"),
        picture=payload.get("picture"),
        person_id=person_id,
        roles=roles,
    )


async def get_current_member(request: Request) -> MemberUser | None:
    """Extract member from Authorization: Bearer <token> header."""
    from app.database import SessionLocal

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    db = SessionLocal()
    try:
        return await get_member_from_token(token, db)
    finally:
        db.close()


async def require_member(
    member: Annotated[MemberUser | None, Depends(get_current_member)],
) -> MemberUser:
    """Dependency that requires member authentication."""
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return member


def require_ministry_role(*allowed_roles: str):
    """Dependency factory: require the member has a specific role in the target ministry."""

    async def _check(
        member: Annotated[MemberUser, Depends(require_member)],
        ministry_id: int | None = None,
    ) -> MemberUser:
        if ministry_id is None:
            return member

        matching = [
            r
            for r in member.roles
            if r["ministry_id"] == ministry_id and r["role"] in allowed_roles
        ]
        if not matching:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)} in this ministry",
            )
        return member

    return _check
