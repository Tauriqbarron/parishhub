# Ministries Event System — Full Build Plan

## What Exists

- `MinistryEvent` model: title, description, event_date, location
- `MinistryEventAttendance` model: event_id, person_id, attended (bool)
- Basic CRUD endpoints for events
- Basic event list in the Ministries Portal group detail page
- No event detail page, no attendance UI, no RSVP, no recurrence, no time, no capacity

## What We're Building

A full event management system for church ministries: recurring events with times, RSVP tracking, capacity limits, attendance sheets, and event categories.

---

## Phase 1: Schema Changes

### 1a. Expand MinistryEvent model
**File:** `backend/app/models/ministry.py`

Add columns to `MinistryEvent`:
```python
start_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # "19:00"
end_time: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)    # "21:00"
event_type: Mapped[str] = mapped_column(String(50), default="other", nullable=False)  # service|meeting|social|outreach|other
capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # null = unlimited
recurrence_rule: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)  # "FREQ=WEEKLY;BYDAY=WE"
recurrence_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
```

### 1b. Create EventRSVP model
**File:** `backend/app/models/ministry.py`

```python
class EventRSVP(Base):
    __tablename__ = "event_rsvps"
    __table_args__ = (UniqueConstraint("event_id", "person_id", name="uq_event_rsvp_person"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("ministry_events.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # "going", "not_going", "maybe"
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    event: Mapped["MinistryEvent"] = relationship("MinistryEvent", back_populates="rsvps")
    person: Mapped["Person"] = relationship("Person", foreign_keys=[person_id])
```

Also add `rsvps` relationship to `MinistryEvent`:
```python
rsvps: Mapped[list["EventRSVP"]] = relationship("EventRSVP", back_populates="event", cascade="all, delete-orphan")
```

### 1c. Alembic migration
Generate and verify the migration covers all new columns and the new table.

---

## Phase 2: Backend API Updates

### 2a. Update event schemas
**File:** `backend/app/schemas/ministry.py`

Update `MinistryEventCreate` to include: start_time, end_time, event_type, capacity, recurrence_rule, recurrence_end
Update `MinistryEventResponse` to include: all new fields + rsvp_count, spots_remaining

### 2b. Update event creation endpoint
**File:** `backend/app/routers/member.py`

Update `create_ministry_event` to accept and store new fields.

### 2c. Update event list/detail responses
**File:** `backend/app/routers/member.py`

Update all event serialisation to include: start_time, end_time, event_type, capacity, rsvp_count, spots_remaining, is_cancelled, recurrence_rule

### 2d. Add RSVP endpoints
**File:** `backend/app/routers/member.py`

```
POST   /member/events/{event_id}/rsvp        — RSVP (going/maybe/not_going)
GET    /member/events/{event_id}/rsvps        — List RSVPs (leader only)
GET    /member/events/{event_id}/attendance   — List attendance (leader + member own)
POST   /member/events/{event_id}/attendance   — Record attendance batch (leader only)
```

### 2e. Add event detail endpoint
```
GET    /member/events/{event_id}              — Full event detail with RSVPs + attendance
```

### 2f. Recurrence expansion helper
**File:** `backend/app/services/events.py` (new)

Helper to expand RRULE into date occurrences for the dashboard and event list.

---

## Phase 3: Frontend — Event Creation Form

**File:** `ministries-frontend/src/routes/groups/[id]/+page.svelte`

Enhance the event creation form with:
- Event type selector (service/meeting/social/outreach/other)
- Start time + end time inputs
- Capacity input (optional, number)
- Recurrence selector (none/weekly/biweekly/monthly) + end date

---

## Phase 4: Frontend — Event Detail Page

**File:** `ministries-frontend/src/routes/groups/[id]/events/[eventId]/+page.svelte` (new)

- Event info card (title, date, time, location, type badge, capacity)
- RSVP section (going/maybe/not_going buttons for members)
- Capacity indicator ("3 spots left" / "Full")
- Leader: attendance sheet (checkbox list of members)
- Leader: RSVP summary (X going, Y maybe, Z not going)

---

## Phase 5: Frontend — Event Card Component

**File:** `ministries-frontend/src/lib/components/EventCard.svelte` (new)

Rich event card replacing inline event display:
- Type badge with icon/color
- Date + time range
- Location
- Recurring indicator
- Capacity status
- RSVP status (if user has RSVPed)

---

## Phase 6: API Client Updates

**File:** `ministries-frontend/src/lib/api.ts`

- Update `MinistryEvent` type with new fields
- Add `rsvp()`, `getRsvps()`, `getAttendance()`, `recordAttendance()`, `eventDetail()` methods

---

## Testing

- Unit tests for recurrence expansion
- Integration tests for RSVP (going/maybe/not_going, capacity enforcement)
- Integration tests for attendance batch recording
- Integration tests for event CRUD with new fields
