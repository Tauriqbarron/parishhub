"""Member-facing API endpoints for Ministries frontend."""

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.member import MemberUser, require_member
from app.database import get_db
from app.limiter import limiter
from app.schemas.ministry import AttendanceBatchCreate, EventRSVPCreate
from app.services.audit import AuditService

router = APIRouter(prefix="/api/member", tags=["member"])


# ---------------------------------------------------------------------------
# Current Member
# ---------------------------------------------------------------------------
@router.get("/me")
async def get_me(
    member: Annotated[MemberUser, Depends(require_member)],
):
    """Get current authenticated member (includes roles and person_id)."""
    return member

# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@router.get("/dashboard/week")
async def get_week_dashboard(
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get this week's events across all ministries the user belongs to."""
    from app.models.ministry import Ministry, MinistryEvent

    ministry_ids = [r["ministry_id"] for r in member.roles if r["ministry_id"]]
    if not ministry_ids:
        return {"events": [], "week_start": None, "week_end": None}

    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday

    events = (
        db.query(MinistryEvent)
        .filter(
            MinistryEvent.ministry_id.in_(ministry_ids),
            MinistryEvent.event_date >= week_start,
            MinistryEvent.event_date <= week_end,
        )
        .order_by(MinistryEvent.event_date)
        .all()
    )

    # Enrich with ministry name
    ministry_names = {
        m.id: m.name
        for m in db.query(Ministry)
        .filter(Ministry.id.in_(ministry_ids))
        .all()
    }

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "events": [
            {
                "id": e.id,
                "ministry_id": e.ministry_id,
                "ministry_name": ministry_names.get(e.ministry_id, ""),
                "title": e.title,
                "description": e.description,
                "event_date": e.event_date.isoformat(),
                "location": e.location,
                "attendance_count": len(e.attendance),
            }
            for e in events
        ],
    }


# ---------------------------------------------------------------------------
# My Ministries (groups)
# ---------------------------------------------------------------------------
@router.get("/ministries")
async def get_my_ministries(
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get ministries where the user is a leader or member."""
    from app.models.ministry import Ministry

    ministry_ids = list({r["ministry_id"] for r in member.roles if r["ministry_id"]})
    if not ministry_ids:
        return {"ministries": []}

    ministries = (
        db.query(Ministry).filter(Ministry.id.in_(ministry_ids)).all()
    )

    result = []
    for m in ministries:
        user_role = next(
            (r["role"] for r in member.roles if r["ministry_id"] == m.id), None
        )
        result.append(
            {
                "id": m.id,
                "name": m.name,
                "description": m.description,
                "is_active": m.is_active,
                "user_role": user_role,
                "member_count": len(m.members),
            }
        )

    return {"ministries": result}


@router.get("/ministries/{ministry_id}")
async def get_ministry_detail(
    ministry_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get ministry detail if user has access."""
    from app.models.ministry import Ministry

    # Check access
    user_ministry_ids = {r["ministry_id"] for r in member.roles if r["ministry_id"]}
    if ministry_id not in user_ministry_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this ministry",
        )

    ministry = db.get(Ministry, ministry_id)
    if not ministry:
        raise HTTPException(status_code=404, detail="Ministry not found")

    user_role = next(
        (r["role"] for r in member.roles if r["ministry_id"] == ministry_id), None
    )

    return {
        "id": ministry.id,
        "name": ministry.name,
        "description": ministry.description,
        "is_active": ministry.is_active,
        "user_role": user_role,
        "members": [
            {
                "id": mem.id,
                "person_id": mem.person_id,
                "person_name": f"{mem.person.first_name} {mem.person.last_name}" if mem.person else None,
                "role": mem.role,
                "joined_date": mem.joined_date.isoformat() if mem.joined_date else None,
                "is_active": mem.is_active,
                # Full person record from the unified people table - ministries portal displays these fields
                "person": {
                    "id": mem.person.id,
                    "first_name": mem.person.first_name,
                    "middle_name": mem.person.middle_name,
                    "last_name": mem.person.last_name,
                    "date_of_birth": mem.person.date_of_birth.isoformat() if mem.person.date_of_birth else None,
                    "gender": mem.person.gender.value if mem.person.gender else None,
                    "email": mem.person.email,
                    "phone": mem.person.phone,
                    "address_line1": mem.person.address_line1,
                    "address_line2": mem.person.address_line2,
                    "city": mem.person.city,
                    "postal_code": mem.person.postal_code,
                    "notes": mem.person.notes,
                } if mem.person else None,
            }
            for mem in ministry.members
        ],
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "event_date": e.event_date.isoformat(),
                "location": e.location,
                "attendance_count": len(e.attendance),
            }
            for e in ministry.events
        ],
    }


# ---------------------------------------------------------------------------
# Member Management (leader only)
# ---------------------------------------------------------------------------
class AddMemberRequest(BaseModel):
    email: str | None = None
    name: str | None = None
    person_id: int | None = None
    role: str = "member"


@router.post("/ministries/{ministry_id}/members")
@limiter.limit("30/minute")
async def add_ministry_member(
    request: Request,
    ministry_id: int,
    body: AddMemberRequest,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader adds a member to their ministry. Accepts person_id or email."""
    from app.models.ministry import Ministry, MinistryMember, UserRole
    from app.models.person import Person

    # Check user is leader (or admin) for this ministry
    user_roles_for_ministry = [
        r for r in member.roles if r["ministry_id"] == ministry_id and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not user_roles_for_ministry:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ministry leaders can add members",
        )

    ministry = db.get(Ministry, ministry_id)
    if not ministry:
        raise HTTPException(status_code=404, detail="Ministry not found")

    # Resolve person — by ID or by email
    if body.person_id:
        person = db.get(Person, body.person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
    elif body.email:
        person = db.query(Person).filter(Person.email == body.email).first()
        if not person:
            # Create a minimal Person record
            name_parts = (body.name or body.email.split("@")[0]).split(" ", 1)
            person = Person(
                first_name=name_parts[0],
                last_name=name_parts[1] if len(name_parts) > 1 else "",
                email=body.email,
            )
            db.add(person)
            db.flush()
    else:
        raise HTTPException(status_code=400, detail="Either person_id or email is required")

    # Check if already a member
    existing = (
        db.query(MinistryMember)
        .filter(
            MinistryMember.ministry_id == ministry_id,
            MinistryMember.person_id == person.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Person is already a member of this ministry")

    # Members Portal always adds as "member" — admin portal handles leader/co-leader separately
    assigned_role = "member"

    # Add membership
    membership = MinistryMember(
        ministry_id=ministry_id,
        person_id=person.id,
        role=assigned_role,
        joined_date=date.today(),
    )
    db.add(membership)

    # Add user_role for login access (use person.email, not body.email — body.email is None when person_id is used)
    person_email = person.email or body.email
    if person_email:
        existing_role = (
            db.query(UserRole)
            .filter(
                UserRole.user_email == person_email,
                UserRole.role == assigned_role,
                UserRole.ministry_id == ministry_id,
            )
            .first()
        )
        if not existing_role:
            user_role = UserRole(
                user_email=person_email,
                role=assigned_role,
                ministry_id=ministry_id,
            )
            db.add(user_role)

    AuditService(db).log_create(
        resource_type="ministry_member",
        resource_id=ministry_id,
        new_values={"person_id": person.id, "person_name": f"{person.first_name} {person.last_name}", "role": assigned_role},
        user_email=member.email,
        description=f"Added {person_email or person.first_name} to ministry {ministry_id}",
    )

    db.commit()
    db.refresh(membership)

    return {
        "id": membership.id,
        "person_id": person.id,
        "person_name": f"{person.first_name} {person.last_name}",
        "role": membership.role,
        "joined_date": membership.joined_date.isoformat(),
        "message": f"{person_email or person.first_name} added to {ministry.name}",
    }


@router.delete("/ministries/{ministry_id}/members/{member_id}")
async def remove_ministry_member(
    ministry_id: int,
    member_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader removes a member from their ministry."""
    from app.models.ministry import MinistryMember, UserRole

    # Check user is leader
    user_roles_for_ministry = [
        r for r in member.roles if r["ministry_id"] == ministry_id and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not user_roles_for_ministry:
        raise HTTPException(status_code=403, detail="Only ministry leaders can remove members")

    membership = db.get(MinistryMember, member_id)
    if not membership or membership.ministry_id != ministry_id:
        raise HTTPException(status_code=404, detail="Membership not found")

    # Remove user_role too
    person_email = membership.person.email if membership.person else None
    if person_email:
        db.query(UserRole).filter(
            UserRole.user_email == person_email,
            UserRole.ministry_id == ministry_id,
        ).delete()

    AuditService(db).log_delete(
        resource_type="ministry_member",
        resource_id=ministry_id,
        old_values={"member_id": member_id, "person_email": person_email},
        user_email=member.email,
        description=f"Removed member {member_id} from ministry {ministry_id}",
    )

    db.delete(membership)
    db.commit()

    return {"message": "Member removed"}


class UpdateMemberRoleRequest(BaseModel):
    role: str


@router.patch("/ministries/{ministry_id}/members/{person_id}")
async def update_member_role(
    ministry_id: int,
    person_id: int,
    body: UpdateMemberRoleRequest,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader or co-leader updates a member's role. Co-leaders cannot promote to leader."""
    from app.models.ministry import MinistryMember, UserRole
    from app.models.person import Person

    # Validate role
    if body.role not in ("member", "leader", "co-leader"):
        raise HTTPException(
            status_code=400,
            detail="Role must be one of: member, leader, co-leader",
        )

    # Check user is leader or co-leader for this ministry
    user_roles_for_ministry = [
        r for r in member.roles
        if r["ministry_id"] == ministry_id
        and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not user_roles_for_ministry:
        raise HTTPException(
            status_code=403,
            detail="Only ministry leaders can update member roles",
        )

    # Co-leaders cannot promote anyone to leader
    is_co_leader = all(r["role"] == "co-leader" for r in user_roles_for_ministry)
    if is_co_leader and body.role == "leader":
        raise HTTPException(
            status_code=403,
            detail="Co-leaders cannot promote members to leader",
        )

    # Find the membership by person_id
    membership = (
        db.query(MinistryMember)
        .filter(
            MinistryMember.ministry_id == ministry_id,
            MinistryMember.person_id == person_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    old_role = membership.role

    # Update membership role
    membership.role = body.role

    # Sync user_roles table
    person = membership.person
    if person and person.email:
        # Remove old role
        db.query(UserRole).filter(
            UserRole.user_email == person.email,
            UserRole.ministry_id == ministry_id,
            UserRole.role == old_role,
        ).delete()
        # Add new role
        existing = (
            db.query(UserRole)
            .filter(
                UserRole.user_email == person.email,
                UserRole.ministry_id == ministry_id,
                UserRole.role == body.role,
            )
            .first()
        )
        if not existing:
            db.add(UserRole(
                user_email=person.email,
                role=body.role,
                ministry_id=ministry_id,
            ))

    AuditService(db).log_update(
        resource_type="ministry_member",
        resource_id=ministry_id,
        old_values={"person_id": person_id, "role": old_role},
        new_values={"person_id": person_id, "role": body.role},
        user_email=member.email,
        description=f"Changed role of person {person_id} from {old_role} to {body.role} in ministry {ministry_id}",
    )

    db.commit()
    db.refresh(membership)

    return {
        "person_id": person_id,
        "role": body.role,
        "message": f"Role updated to {body.role}",
        "person_name": f"{person.first_name} {person.last_name}" if person else None,
    }


# ---------------------------------------------------------------------------
# Events (leader can create, all can view)
# ---------------------------------------------------------------------------
class CreateEventRequest(BaseModel):
    title: str
    description: str | None = None
    event_date: date
    location: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    event_type: str = "other"
    capacity: int | None = None
    recurrence_rule: str | None = None
    recurrence_end: date | None = None


@router.get("/ministries/{ministry_id}/events")
async def list_ministry_events(
    ministry_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """List events for a ministry the user belongs to."""
    from app.models.ministry import MinistryEvent
    from app.services.ministry import MinistryService
    from datetime import date as date_type, timedelta as td

    user_ministry_ids = {r["ministry_id"] for r in member.roles if r["ministry_id"]}
    if ministry_id not in user_ministry_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    events = (
        db.query(MinistryEvent)
        .filter(MinistryEvent.ministry_id == ministry_id)
        .order_by(MinistryEvent.event_date.desc())
        .all()
    )

    # Expand recurring events — show from today forward
    today = date_type.today()
    far_future = today + td(days=365)
    expanded = MinistryService.expand_recurring_events(events, today, far_future)

    return {
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "event_date": e.event_date.isoformat(),
                "location": e.location,
                "attendance_count": len(e.attendance) if e.attendance else 0,
            }
            for e in expanded
        ]
    }



@router.get("/events")
async def list_member_events(
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
    date_from: date | None = None,
    date_to: date | None = None,
):
    """List events across all ministries the user belongs to, with RSVP status."""
    from app.models.ministry import MinistryEvent, Ministry, EventRSVP
    from app.models.person import Person

    user_ministry_ids = {r["ministry_id"] for r in member.roles if r["ministry_id"]}
    if not user_ministry_ids:
        return []

    # Get person record for RSVP lookup
    person = db.query(Person).filter(Person.email == member.email).first()
    user_rsvp_map = {}
    if person:
        rsvps = (
            db.query(EventRSVP)
            .filter(EventRSVP.person_id == person.id)
            .all()
        )
        user_rsvp_map = {r.event_id: r.status for r in rsvps}

    # Ministry names
    ministry_names = {
        m.id: m.name
        for m in db.query(Ministry).filter(Ministry.id.in_(user_ministry_ids)).all()
    }

    query = db.query(MinistryEvent).filter(MinistryEvent.ministry_id.in_(user_ministry_ids))
    # NOTE: date filters are NOT applied to the DB query — recurring events
    # with original dates outside the range must still be loaded for expansion.

    # Group by event to count RSVPs per event
    from sqlalchemy import func
    rsvp_counts = (
        db.query(
            EventRSVP.event_id,
            func.count().label("going_count")
        )
        .filter(EventRSVP.status == "going")
        .group_by(EventRSVP.event_id)
        .all()
    )
    # DEBUG: log the raw result
    import sys
    print(f"\n[DEBUG list_member_events] rsvp_counts raw: {rsvp_counts}", file=sys.stderr)
    rsvp_count_map = {eid: count for eid, count in rsvp_counts}
    print(f"[DEBUG] rsvp_count_map: {rsvp_count_map}", file=sys.stderr)

    events = query.order_by(MinistryEvent.event_date).all()

    # Expand recurring events within the requested date range
    # If only date_from is given, default date_to to 1 year out
    from app.services.ministry import MinistryService
    from datetime import timedelta as td
    effective_date_to = date_to or (date_from + td(days=365) if date_from else None)
    expanded_events = MinistryService.expand_recurring_events(events, date_from, effective_date_to)

    result = []
    for e in expanded_events:
        result.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "event_date": e.event_date.isoformat(),
            "start_time": e.start_time,
            "end_time": e.end_time,
            "location": e.location,
            "event_type": e.event_type,
            "capacity": e.capacity,
            "is_cancelled": e.is_cancelled,
            "attendance_count": len(e.attendance) if e.attendance else 0,
            "ministry_id": e.ministry_id,
            "ministry_name": ministry_names.get(e.ministry_id, ""),
            "user_rsvp": user_rsvp_map.get(e.id),
            "rsvp_count": rsvp_count_map.get(e.id, 0),
        })
    return result

@router.post("/ministries/{ministry_id}/events")
@limiter.limit("30/minute")
async def create_ministry_event(
    request: Request,
    ministry_id: int,
    body: CreateEventRequest,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader creates an event for their ministry."""
    from app.models.ministry import MinistryEvent

    user_roles_for_ministry = [
        r for r in member.roles if r["ministry_id"] == ministry_id and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not user_roles_for_ministry:
        raise HTTPException(status_code=403, detail="Only leaders can create events")

    event = MinistryEvent(
        ministry_id=ministry_id,
        title=body.title,
        description=body.description,
        event_date=body.event_date,
        location=body.location,
        start_time=body.start_time,
        end_time=body.end_time,
        event_type=body.event_type,
        capacity=body.capacity,
        recurrence_rule=body.recurrence_rule,
        recurrence_end=body.recurrence_end,
    )
    db.add(event)

    AuditService(db).log_create(
        resource_type="ministry_event",
        resource_id=ministry_id,
        new_values={"title": body.title, "event_date": body.event_date.isoformat(), "event_type": body.event_type},
        user_email=member.email,
        description=f"Created event '{body.title}' for ministry {ministry_id}",
    )

    db.commit()
    db.refresh(event)

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "event_date": event.event_date.isoformat(),
        "location": event.location,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "event_type": event.event_type,
        "capacity": event.capacity,
        "recurrence_rule": event.recurrence_rule,
        "recurrence_end": event.recurrence_end.isoformat() if event.recurrence_end else None,
        "is_cancelled": event.is_cancelled,
        "rsvp_count": 0,
        "spots_remaining": event.capacity,
        "attendance_count": 0,
    }


class UpdateEventRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    event_date: date | None = None
    location: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    event_type: str | None = None
    capacity: int | None = None
    recurrence_rule: str | None = None
    recurrence_end: date | None = None
    is_cancelled: bool | None = None


@router.put("/events/{event_id}")
@limiter.limit("30/minute")
async def update_ministry_event(
    request: Request,
    event_id: int,
    body: UpdateEventRequest,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader updates an event."""
    from app.models.ministry import MinistryEvent

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check user is leader of this ministry
    user_roles_for_ministry = [
        r for r in member.roles if r["ministry_id"] == event.ministry_id and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not user_roles_for_ministry:
        raise HTTPException(status_code=403, detail="Only leaders can edit events")

    update_data = body.model_dump(exclude_unset=True)

    # Capture old values before mutation
    old_values = {
        "title": event.title,
        "description": event.description,
        "event_date": event.event_date.isoformat(),
        "event_type": event.event_type,
        "location": event.location,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "capacity": event.capacity,
        "recurrence_rule": event.recurrence_rule,
        "recurrence_end": event.recurrence_end.isoformat() if event.recurrence_end else None,
        "is_cancelled": event.is_cancelled,
    }

    for field, value in update_data.items():
        setattr(event, field, value)

    # Convert date objects to strings for audit (JSON column)
    audit_new = {}
    for k, v in update_data.items():
        if isinstance(v, date):
            audit_new[k] = v.isoformat()
        else:
            audit_new[k] = v

    AuditService(db).log_update(
        resource_type="ministry_event",
        resource_id=event_id,
        old_values=old_values,
        new_values=audit_new,
        user_email=member.email,
        description=f"Updated event '{event.title}'",
    )

    db.commit()
    db.refresh(event)

    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "event_date": event.event_date.isoformat(),
        "location": event.location,
        "start_time": event.start_time,
        "end_time": event.end_time,
        "event_type": event.event_type,
        "capacity": event.capacity,
        "recurrence_rule": event.recurrence_rule,
        "recurrence_end": event.recurrence_end.isoformat() if event.recurrence_end else None,
        "is_cancelled": event.is_cancelled,
        "attendance_count": len(event.attendance),
    }


@router.delete("/events/{event_id}")
@limiter.limit("30/minute")
async def delete_ministry_event(
    request: Request,
    event_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader deletes an event."""
    from app.models.ministry import MinistryEvent

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check user is leader of this ministry
    user_roles_for_ministry = [
        r for r in member.roles if r["ministry_id"] == event.ministry_id and r["role"] in ("leader", "admin", "co-leader")
    ]
    if not user_roles_for_ministry:
        raise HTTPException(status_code=403, detail="Only leaders can delete events")

    AuditService(db).log_delete(
        resource_type="ministry_event",
        resource_id=event_id,
        old_values={"title": event.title, "event_date": event.event_date.isoformat()},
        user_email=member.email,
        description=f"Deleted event '{event.title}'",
    )

    db.delete(event)
    db.commit()

    return {"deleted": True}


@router.get("/persons/search")
@limiter.limit("30/minute")
async def search_persons(
    request: Request,
    q: str,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Search persons by name for adding to ministries."""
    from app.models.person import Person
    from sqlalchemy import or_

    if len(q.strip()) < 2:
        return {"items": []}

    search = f"%{q.strip()}%"
    persons = (
        db.query(Person)
        .filter(
            or_(
                Person.first_name.ilike(search),
                Person.last_name.ilike(search),
            )
        )
        .limit(10)
        .all()
    )

    return {
        "items": [
            {
                "id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "email": p.email,
            }
            for p in persons
        ]
    }


# ---------------------------------------------------------------------------
# Event Detail
# ---------------------------------------------------------------------------
@router.get("/events/{event_id}")
async def get_event_detail(
    event_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get full event detail with RSVP and attendance."""
    from app.models.ministry import (
        EventRSVP,
        MinistryEvent,
        MinistryEventAttendance,
    )

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check access
    user_ministry_ids = {r["ministry_id"] for r in member.roles if r["ministry_id"]}
    if event.ministry_id not in user_ministry_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    is_leader = any(
        r["ministry_id"] == event.ministry_id and r["role"] in ("leader", "admin", "co-leader")
        for r in member.roles
    )

    # Get user's RSVP
    from app.models.person import Person

    person = db.query(Person).filter(Person.email == member.email).first()
    user_rsvp = None
    if person:
        rsvp = (
            db.query(EventRSVP)
            .filter(EventRSVP.event_id == event_id, EventRSVP.person_id == person.id)
            .first()
        )
        if rsvp:
            user_rsvp = rsvp.status

    # RSVP counts
    rsvps = db.query(EventRSVP).filter(EventRSVP.event_id == event_id).all()
    going_count = len([r for r in rsvps if r.status == "going"])
    maybe_count = len([r for r in rsvps if r.status == "maybe"])
    not_going_count = len([r for r in rsvps if r.status == "not_going"])
    spots_remaining = max(0, event.capacity - going_count) if event.capacity else None

    # Attendance
    attendance_records = (
        db.query(MinistryEventAttendance)
        .filter(MinistryEventAttendance.event_id == event_id)
        .all()
    )

    # RSVP list (leader only)
    rsvp_list = []
    if is_leader:
        for r in rsvps:
            rsvp_list.append({
                "id": r.id,
                "person_id": r.person_id,
                "person_name": f"{r.person.first_name} {r.person.last_name}" if r.person else None,
                "status": r.status,
            })

    return {
        "id": event.id,
        "ministry_id": event.ministry_id,
        "title": event.title,
        "description": event.description,
        "event_date": event.event_date.isoformat(),
        "start_time": event.start_time,
        "end_time": event.end_time,
        "location": event.location,
        "event_type": event.event_type,
        "capacity": event.capacity,
        "is_cancelled": event.is_cancelled,
        "recurrence_rule": event.recurrence_rule,
        "recurrence_end": event.recurrence_end.isoformat() if event.recurrence_end else None,
        "rsvp_count": going_count,
        "spots_remaining": spots_remaining,
        "attendance_count": len(attendance_records),
        "user_rsvp": user_rsvp,
        "rsvp_summary": {
            "going": going_count,
            "maybe": maybe_count,
            "not_going": not_going_count,
        },
        "rsvps": rsvp_list,
        "attendance": [
            {
                "person_id": a.person_id,
                "person_name": f"{a.person.first_name} {a.person.last_name}" if a.person else None,
                "attended": a.attended,
            }
            for a in attendance_records
        ],
    }


# ---------------------------------------------------------------------------
# RSVP
# ---------------------------------------------------------------------------
@router.post("/events/{event_id}/rsvp")
@limiter.limit("30/minute")
async def rsvp_event(
    request: Request,
    event_id: int,
    body: EventRSVPCreate,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """RSVP to an event (going/maybe/not_going)."""
    from app.models.ministry import EventRSVP, MinistryEvent
    from app.models.person import Person

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check access
    user_ministry_ids = {r["ministry_id"] for r in member.roles if r["ministry_id"]}
    if event.ministry_id not in user_ministry_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    # Validate status
    if body.status not in ("going", "not_going", "maybe"):
        raise HTTPException(status_code=400, detail="Status must be going, not_going, or maybe")

    # Find person
    person = db.query(Person).filter(Person.email == member.email).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Check capacity
    if body.status == "going" and event.capacity:
        going_count = (
            db.query(EventRSVP)
            .filter(EventRSVP.event_id == event_id, EventRSVP.status == "going")
            .count()
        )
        # Allow if already going (updating RSVP)
        existing = (
            db.query(EventRSVP)
            .filter(EventRSVP.event_id == event_id, EventRSVP.person_id == person.id)
            .first()
        )
        if not existing or existing.status != "going":
            if going_count >= event.capacity:
                raise HTTPException(status_code=400, detail="Event is full")

    # Upsert RSVP
    existing = (
        db.query(EventRSVP)
        .filter(EventRSVP.event_id == event_id, EventRSVP.person_id == person.id)
        .first()
    )
    if existing:
        existing.status = body.status
        rsvp = existing
    else:
        rsvp = EventRSVP(event_id=event_id, person_id=person.id, status=body.status)
        db.add(rsvp)

    AuditService(db).log_update(
        resource_type="event_rsvp",
        resource_id=event_id,
        old_values={"status": existing.status} if existing else {},
        new_values={"status": body.status, "person_id": person.id},
        user_email=member.email,
        description=f"RSVP '{body.status}' for event {event_id}",
    )

    db.commit()
    db.refresh(rsvp)

    # Recalculate counts
    going_count = (
        db.query(EventRSVP)
        .filter(EventRSVP.event_id == event_id, EventRSVP.status == "going")
        .count()
    )
    spots_remaining = max(0, event.capacity - going_count) if event.capacity else None

    return {
        "id": rsvp.id,
        "status": rsvp.status,
        "rsvp_count": going_count,
        "spots_remaining": spots_remaining,
    }


@router.get("/events/{event_id}/rsvps")
async def get_event_rsvps(
    event_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader: get all RSVPs for an event."""
    from app.models.ministry import EventRSVP, MinistryEvent

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check leader access
    is_leader = any(
        r["ministry_id"] == event.ministry_id and r["role"] in ("leader", "admin", "co-leader")
        for r in member.roles
    )
    if not is_leader:
        raise HTTPException(status_code=403, detail="Only leaders can view RSVPs")

    rsvps = db.query(EventRSVP).filter(EventRSVP.event_id == event_id).all()

    going_count = len([r for r in rsvps if r.status == "going"])
    maybe_count = len([r for r in rsvps if r.status == "maybe"])
    not_going_count = len([r for r in rsvps if r.status == "not_going"])

    return {
        "rsvps": [
            {
                "id": r.id,
                "event_id": r.event_id,
                "person_id": r.person_id,
                "person_name": f"{r.person.first_name} {r.person.last_name}" if r.person else None,
                "status": r.status,
            }
            for r in rsvps
        ],
        "going_count": going_count,
        "maybe_count": maybe_count,
        "not_going_count": not_going_count,
    }


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------
@router.post("/events/{event_id}/attendance")
@limiter.limit("30/minute")
async def record_attendance(
    request: Request,
    event_id: int,
    body: AttendanceBatchCreate,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Leader: record attendance for an event."""
    from app.models.ministry import MinistryEvent, MinistryEventAttendance

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check leader access
    is_leader = any(
        r["ministry_id"] == event.ministry_id and r["role"] in ("leader", "admin", "co-leader")
        for r in member.roles
    )
    if not is_leader:
        raise HTTPException(status_code=403, detail="Only leaders can record attendance")

    recorded = 0
    for person_id in body.person_ids:
        existing = (
            db.query(MinistryEventAttendance)
            .filter(
                MinistryEventAttendance.event_id == event_id,
                MinistryEventAttendance.person_id == person_id,
            )
            .first()
        )
        if not existing:
            attendance = MinistryEventAttendance(
                event_id=event_id,
                person_id=person_id,
                attended=True,
            )
            db.add(attendance)
            recorded += 1

    AuditService(db).log_update(
        resource_type="event_attendance",
        resource_id=event_id,
        old_values={},
        new_values={"person_ids": list(body.person_ids), "recorded_count": recorded},
        user_email=member.email,
        description=f"Recorded attendance for {recorded} people at event {event_id}",
    )

    db.commit()
    return {"recorded": recorded}


@router.get("/events/{event_id}/attendance")
async def get_event_attendance(
    event_id: int,
    member: Annotated[MemberUser, Depends(require_member)],
    db: Annotated[Session, Depends(get_db)],
):
    """Get attendance for an event."""
    from app.models.ministry import MinistryEvent, MinistryEventAttendance

    event = db.get(MinistryEvent, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check access
    user_ministry_ids = {r["ministry_id"] for r in member.roles if r["ministry_id"]}
    if event.ministry_id not in user_ministry_ids:
        raise HTTPException(status_code=403, detail="Access denied")

    records = (
        db.query(MinistryEventAttendance)
        .filter(MinistryEventAttendance.event_id == event_id)
        .all()
    )

    return {
        "attendance": [
            {
                "person_id": r.person_id,
                "person_name": f"{r.person.first_name} {r.person.last_name}" if r.person else None,
                "attended": r.attended,
            }
            for r in records
        ]
    }
