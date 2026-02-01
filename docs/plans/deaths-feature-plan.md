# Deaths Feature Implementation Plan

## Architecture Overview

Deaths implemented as **separate table** (not sacrament extension) - death is a life event, not a sacrament.

Pattern: Schemas (Pydantic) → Models (SQLAlchemy) → Services (CRUD) → Routers (API)

---

## Phase 1: Backend Model

**New file: `backend/app/models/death.py`**

```python
# Fields:
- id: Primary key
- person_id: ForeignKey to persons.id (required, unique - one death per person)
- date_of_death: Date (required)
- place_of_death: String (optional)
- cause_of_death: String (optional)
- burial_date: Date (optional)
- burial_location: String (optional)
- funeral_date: Date (optional)
- funeral_location: String (optional)
- officiating_priest_id: ForeignKey to persons.id (optional)
- notes: Text (optional)
- created_at, updated_at: DateTime timestamps
```

**Modify: `backend/app/models/person.py`**
- Add relationship: `death: Mapped[Optional["Death"]] = relationship("Death", back_populates="person", uselist=False)`

---

## Phase 2: Backend Schemas

**New file: `backend/app/schemas/death.py`**

- DeathBase, DeathCreate, DeathUpdate, DeathResponse, DeathWithPerson, DeathStatistics

---

## Phase 3: Backend Service

**New file: `backend/app/services/death.py`**

```python
class DeathService:
    - create(): Create death record
    - get_by_id(), get_by_person_id(), get_list()
    - update(), delete()
    - get_statistics()
```

Validations:
- Person exists
- Person doesn't already have death record
- date_of_death not in future
- date_of_death after person's date_of_birth

---

## Phase 4: Backend Router

**New file: `backend/app/routers/deaths.py`**

```
POST   /api/deaths              - Create death record
GET    /api/deaths              - List deaths (paginated, filtered)
GET    /api/deaths/statistics   - Get statistics
GET    /api/deaths/{id}         - Get single record
PUT    /api/deaths/{id}         - Update
DELETE /api/deaths/{id}         - Delete

POST   /api/persons/{id}/death  - Record death for person
GET    /api/persons/{id}/death  - Get death for person
```

**Modify: `backend/app/main.py`** - Register router

---

## Phase 5: Database Migration

**New migration: `add_deaths_table.py`**

```python
op.create_table('deaths', ...)
op.create_index('ix_deaths_date_of_death', 'deaths', ['date_of_death'])
op.create_index('ix_deaths_person_id', 'deaths', ['person_id'])
```

---

## Phase 6: Frontend API

**Modify: `frontend/src/lib/api.ts`**

Add types: Death, DeathCreate, DeathStatistics
Add API: deathsApi.list(), get(), create(), update(), delete(), getStatistics(), getForPerson()

---

## Phase 7: Frontend Components

**New files:**
- `src/lib/components/DeathRecord.svelte` - Display death info on person detail
- `src/lib/components/DeathForm.svelte` - Modal form for recording death

---

## Phase 8: Frontend Routes

**Modify:** `src/routes/people/[id]/+page.svelte` - Add DeathRecord component
**New:** `src/routes/analytics/deaths/new/+page.svelte` - New death form page
**Modify:** `src/routes/analytics/+page.svelte` - Add Deaths tab

---

## Phase 9: UI Integration

- PersonHeader.svelte - Add "Deceased" badge
- PersonTable.svelte - Add deceased status indicator
- PersonFilters - Add `is_deceased` filter

---

## Phase 10: Statistics Integration

- `backend/app/routers/statistics.py` - Add deaths_this_year
- Dashboard - Add deaths stat card

---

## Implementation Order

1. Backend Model & Migration
2. Backend Schemas
3. Backend Service
4. Backend Router
5. Frontend API types/functions
6. Frontend Components
7. Frontend Routes/Pages
8. UI Integration
9. Statistics Integration

---

## Reference Files (patterns to follow)

- `backend/app/models/analytics.py` - Birth model pattern
- `backend/app/schemas/analytics.py` - Schema pattern
- `backend/app/services/analytics.py` - BirthService pattern
- `backend/app/routers/analytics.py` - Router pattern
- `frontend/src/lib/api.ts` - API client pattern
