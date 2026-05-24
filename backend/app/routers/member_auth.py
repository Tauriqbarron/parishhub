"""Member authentication endpoints for Ministries frontend."""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.auth.member import (
    MemberUser,
    create_member_token,
    verify_google_token,
)
from app.limiter import limiter

router = APIRouter(prefix="/api/auth/member", tags=["member-auth"])


class GoogleLoginRequest(BaseModel):
    """Request body for Google login."""

    id_token: str


class LoginResponse(BaseModel):
    """Response after successful login."""

    token: str
    user: MemberUser


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def member_google_login(request: Request, body: GoogleLoginRequest):
    """Sign in with Google. Verifies token, checks user has a ministry role, issues JWT."""
    from app.database import SessionLocal
    from app.models.ministry import MinistryMember, UserRole

    # Verify Google token
    google_user = await verify_google_token(body.id_token)
    if not google_user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google email not verified",
        )

    email = google_user["email"]

    # Check user has at least one role in any ministry
    db = SessionLocal()
    try:
        roles = db.query(UserRole).filter(UserRole.user_email == email).all()
        role_list = [{"role": r.role, "ministry_id": r.ministry_id} for r in roles]

        # Also check ministry_members table (by email match on Person)
        from app.models.person import Person

        person = db.query(Person).filter(Person.email == email).first()
        if person:
            memberships = (
                db.query(MinistryMember)
                .filter(MinistryMember.person_id == person.id)
                .all()
            )
            for m in memberships:
                entry = {"role": m.role, "ministry_id": m.ministry_id}
                if entry not in role_list:
                    role_list.append(entry)

        if not role_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You haven't been added to any ministry yet. Contact your group leader.",
            )

        # Issue JWT
        token = create_member_token(
            email=email,
            name=google_user.get("name"),
            picture=google_user.get("picture"),
        )

        user = MemberUser(
            email=email,
            name=google_user.get("name"),
            picture=google_user.get("picture"),
            person_id=person.id if person else None,
            roles=role_list,
        )

        return LoginResponse(token=token, user=user)
    finally:
        db.close()


@router.get("/me", response_model=MemberUser)
async def get_me(request: Request):
    """Get current authenticated member with their roles."""
    from app.database import SessionLocal

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = auth_header[7:]
    db = SessionLocal()
    try:
        from app.auth.member import get_member_from_token

        return await get_member_from_token(token, db)
    finally:
        db.close()
