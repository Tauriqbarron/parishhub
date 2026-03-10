# Backend Validation & Security Review — Parish Database

**Date:** 2026-02-18
**Scope:** Backend input/output validation, injection protection, auth, error handling

## Context

This is a security audit of the Parish Database application's backend validation layer. The application is a **FastAPI + SQLAlchemy + PostgreSQL** backend consumed by a **SvelteKit** frontend, designed for managing parish member records, households, sacraments, and analytics. The goal is to assess how well the backend protects itself against input and output dangers (injection, XSS, CSRF, data integrity, information leakage, etc.).

---

## Overall Verdict: STRONG — with actionable gaps

The backend demonstrates **solid security fundamentals**. Pydantic enforces typed/constrained input on every endpoint, SQLAlchemy prevents SQL injection, and HMAC-signed auth headers prevent spoofing. However, there are several concrete gaps — particularly around the **public registration endpoint** — that should be addressed.

---

## What's Done Well

### 1. Input Validation via Pydantic (Excellent)
- **Every** POST/PUT endpoint uses typed Pydantic schemas — FastAPI auto-returns 422 for invalid payloads
- String fields have `min_length` / `max_length` constraints throughout:
  - Names: 1–100 chars | Addresses: max 255 | Notes: max 2000 | Postal codes: max 20
- Custom validators for domain rules:
  - Phone regex: `^\+?[\d\s\-().]{7,20}$` — `backend/app/schemas/person.py:9`
  - Date-of-birth not in future — `backend/app/schemas/person.py:24-29`
  - Death date not in future — `backend/app/schemas/death.py:21-26`
  - Attendance/population counts `ge=0` — `backend/app/schemas/analytics.py`
- Query params validated with `ge`, `le`, and regex whitelists:
  - `sort_by` restricted to `^(first_name|last_name|email|created_at|updated_at|date_of_birth)$` — `backend/app/routers/persons.py:91`
  - `per_page` capped at `le=100` — `backend/app/routers/persons.py:75`

### 2. SQL Injection Protection (Excellent)
- **Zero raw SQL** in the entire codebase
- All queries use SQLAlchemy ORM: `select()`, `.where()`, `.ilike()` — fully parameterized
- Search uses `.ilike(search_term)` which is parameterized — `backend/app/services/person.py:73-80`

### 3. Authentication Architecture (Excellent)
- Two-layer auth: **SvelteKit OAuth** (Google) + **HMAC signature verification** on backend
- HMAC uses `hmac.compare_digest()` for timing-safe comparison — `backend/app/auth/dependencies.py:43`
- 5-minute replay window — `backend/app/auth/dependencies.py:31`
- Single authorized email enforced at **both** proxy and backend layers
- `require_auth` dependency consistently applied on all protected routes
- `SECRET_KEY` validated for minimum 32 chars, rejects default values — `backend/app/config.py:32-41`

### 4. Security Headers (Good)
- CSP, X-Frame-Options (DENY), HSTS, X-Content-Type-Options (nosniff), Referrer-Policy all set — `backend/app/main.py:17-26`
- Duplicated in Nginx for production — defense in depth

### 5. Error Handling (Good)
- Generic error messages returned to clients: `"Registration failed. Please try again or contact the parish office."`
- Stack traces logged server-side only (`exc_info=True`), never exposed to users
- Transaction rollback on failure — `backend/app/routers/registration.py:275-284`

### 6. Rate Limiting (Good)
- `slowapi` with 5/minute on public registration endpoint — `backend/app/routers/registration.py:75`

### 7. XSS Protection (Good)
- Backend is API-only (JSON responses), no HTML rendering
- Svelte auto-escapes template output; no `{@html}` with user data found
- CSP restricts script sources to `'self'`

---

## Vulnerabilities & Gaps to Fix

### CRITICAL

#### C1: Registration `email` field lacks format validation
- **File:** `backend/app/schemas/registration.py:22`, `backend/app/schemas/registration.py:61`
- **Issue:** `email: Optional[str] = None` — no `EmailStr` validation, unlike `PersonCreate` which uses `EmailStr`
- **Risk:** Malformed/malicious email strings stored directly in the database
- **Fix:** Change to `email: Optional[EmailStr] = None` in both `RegistrationMember` and `RegistrationSubmission`

#### C2: No list size limits on registration payload
- **File:** `backend/app/schemas/registration.py:62-64`
- **Issue:** `members`, `relationships`, and `sacraments` lists have no max size. An attacker could POST a registration with 10,000 members, causing a long-running DB transaction
- **Risk:** Denial of service via resource exhaustion on a **public, unauthenticated** endpoint
- **Fix:** Add `Field(max_length=50)` (or appropriate limit) to each list field, and add `Field(min_length=1)` to `members` to require at least one member

#### C3: Unbounded `additional_data` dict on sacraments
- **File:** `backend/app/schemas/registration.py:46`
- **Issue:** `additional_data: dict = Field(default_factory=dict)` — arbitrary JSON stored as JSONB with no key/value validation or size limit
- **Risk:** Attacker could stuff megabytes of arbitrary data into each sacrament record
- **Fix:** Add a Pydantic validator to limit dict size (e.g., max 10 keys, max 1000 chars per value) or define a strict schema for allowed keys

### HIGH

#### H1: Error message leaks internal state
- **File:** `backend/app/routers/registration.py:188`
- **Issue:** `detail=f"Invalid sacrament: member temp_id '{sac.member_temp_id}' not found. Available temp_ids: {list(temp_id_to_person_id.keys())}"`
- **Risk:** Exposes internal temp_id mapping to unauthenticated callers
- **Fix:** Remove `Available temp_ids: ...` from the error message

#### H2: LIKE wildcard injection in search
- **File:** `backend/app/services/person.py:73`
- **Issue:** `search_term = f"%{search}%"` — user input is wrapped in `%` but `%` and `_` characters within the input are not escaped. A search for `%` matches everything; `_` matches any single character
- **Risk:** Not a security vulnerability per se, but allows users to craft queries that return unexpected result sets and potentially cause slower DB queries
- **Fix:** Escape `%` and `_` in the search string before wrapping: `search = search.replace('%', '\\%').replace('_', '\\_')`

#### H3: `getattr` on model for dynamic sorting
- **File:** `backend/app/services/person.py:129`
- **Issue:** `sort_column = getattr(Person, sort_by, Person.last_name)` — while `sort_by` is currently validated at the router level with a regex whitelist, using `getattr` on an ORM model is fragile. If the router validation were ever removed or a new router forgot to add it, this becomes an attribute access vulnerability
- **Fix:** Use an explicit allowlist dict in the service layer: `SORT_COLUMNS = {"first_name": Person.first_name, ...}`

### MEDIUM

#### M1: Registration `relationship_type` and `gender` are plain strings
- **File:** `backend/app/schemas/registration.py:33`, `backend/app/schemas/registration.py:20`
- **Issue:** These are validated by mapping lookups at runtime (e.g., `RELATIONSHIP_TYPE_MAP.get()`), but invalid values only produce errors deep in the handler rather than at schema validation time
- **Fix:** Use `Literal["parent", "child", "spouse", "sibling"]` for `relationship_type` and `Literal["male", "female", "other"]` for `gender` in the schema, so Pydantic rejects invalid values at deserialization with a clear 422

#### M2: Registration `church` and `minister` fields have no max length
- **File:** `backend/app/schemas/registration.py:44-45`
- **Issue:** `church: Optional[str] = None` and `minister: Optional[str] = None` — no `max_length` constraint
- **Fix:** Add `Field(max_length=255)` to both

#### M3: CSP allows `'unsafe-inline'` for styles
- **File:** `backend/app/main.py:20`
- **Issue:** `style-src 'self' 'unsafe-inline'` weakens CSP. While needed for some CSS-in-JS, it allows inline style injection
- **Risk:** Low in an API-only backend (CSP mainly matters for HTML responses), but worth tightening if the backend ever serves HTML
- **Fix:** Use nonce-based or hash-based CSP for styles if feasible

#### M4: No rate limiting on authenticated CRUD endpoints
- **Issue:** Only the public registration endpoint has rate limiting. Authenticated endpoints (persons, households, etc.) have no rate limits
- **Risk:** A compromised auth token could be used for rapid enumeration or bulk data extraction
- **Fix:** Add global rate limits for authenticated endpoints (e.g., 60/minute)

#### M5: `RegistrationURLConfig.base_url` accepts any string
- **File:** `backend/app/schemas/registration.py:79`
- **Issue:** `base_url: str = Field(min_length=1)` — no URL format validation. A malicious admin could set this to a `javascript:` or data URI
- **Fix:** Add a `@field_validator` to ensure it starts with `https://` (or `http://` for local dev)

---

## Summary Table

| Category | Rating | Key Finding |
|---|---|---|
| Pydantic input validation | Excellent | Comprehensive on core schemas; gaps in registration |
| SQL injection | Excellent | Zero raw SQL, all parameterized |
| Authentication | Excellent | HMAC + OAuth, timing-safe, replay protection |
| Authorization | Good | Single-user model, consistently enforced |
| Rate limiting | Good | Present on public endpoint; absent on authenticated |
| Error handling | Good | Generic messages; one info leak in registration |
| Security headers | Good | Full set; `unsafe-inline` in CSP |
| XSS | Excellent | JSON-only API + Svelte auto-escaping |
| CSRF | Good | OAuth state + HMAC signatures |
| Registration endpoint | Needs work | Missing email validation, list limits, field constraints |

---

## Recommended Fixes (Priority Order)

1. **Add list size limits** to `RegistrationSubmission.members/relationships/sacraments`
2. **Use `EmailStr`** for email fields in registration schemas
3. **Remove internal state** from error messages in registration
4. **Add `max_length`** to `church`, `minister` fields in `RegistrationSacrament`
5. **Limit `additional_data`** dict size in registration sacraments
6. **Use `Literal` types** for `gender` and `relationship_type` in registration
7. **Escape LIKE wildcards** in search service
8. **Replace `getattr`** with explicit sort column mapping in person service
9. **Add global rate limits** for authenticated endpoints
10. **Validate URL format** on `RegistrationURLConfig.base_url`
