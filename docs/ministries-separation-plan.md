# Ministries Frontend — Separation Plan

## Problem

The Ministries module currently lives inside the ParishHub admin frontend. This conflates two distinct audiences:

- **ParishHub (admin)** — Priests/admins create ministries and assign leaders
- **Ministries (member-facing)** — Leaders manage groups, add members, members see their groups and weekly events

These need separate frontends with separate auth models.

---

## Architecture

```
┌─────────────────────────────────┐     ┌──────────────────────────────────┐
│  ParishHub (admin)              │     │  Ministries (member-facing)      │
│  parishhub.com                  │     │  ministries.parishhub.com        │
│  port 5173 (dev)                │     │  port 5174 (dev)                 │
│                                 │     │                                  │
│  • Create/edit ministries       │     │  • Leader dashboard              │
│  • Assign leaders & co-leaders  │     │  • Add/manage members            │
│  • View all ministries          │     │  • Create/manage events          │
│  • Full admin oversight         │     │  • Member dashboard              │
│                                 │     │  • This week's events            │
│  Auth: Google OAuth + email     │     │  • Attendance tracking           │
│  allowlist (priest/admin only)  │     │                                  │
│                                 │     │  Auth: Google OAuth, any email   │
│                                 │     │  registered as leader or member  │
└─────────────────────────────────┘     └──────────────────────────────────┘
                          │                          │
                          └──────────┬───────────────┘
                                     │
                          ┌──────────▼──────────────┐
                          │  ParishHub API (shared)  │
                          │  api.parishhub.com       │
                          │  port 8000 (dev)         │
                          │                          │
                          │  • /api/ministries/*     │
                          │  • /api/persons/*        │
                          │  • /api/auth/admin/*     │
                          │  • /api/auth/member/*    │
                          └──────────┬──────────────┘
                                     │
                          ┌──────────▼──────────────┐
                          │  PostgreSQL              │
                          │  ministries, members,    │
                          │  events, attendance,     │
                          │  user_roles              │
                          └──────────────────────────┘
```

---

## Auth Model

### ParishHub Admin (existing — unchanged)
- Google OAuth
- Email allowlist (`AUTHORIZED_EMAILS` env var)
- Only priests/admins can sign in

### Ministries Member-Facing (new)
- Google OAuth (separate client or same client, different callback)
- **No email allowlist** — any Google account can sign in
- On first login, check `user_roles` table:
  - If email has a role → sign in, redirect to dashboard
  - If email has no role → show "You haven't been added to any ministry yet. Contact your group leader."
- Roles come from ParishHub admin assigning leaders, or leaders adding members

### How roles get created (existing flow)
1. Admin creates ministry in ParishHub → `ministries` row
2. Admin assigns leader → `user_roles` row (email + role="leader" + ministry_id)
3. Leader logs into Ministries site → sees their ministry
4. Leader adds member → `ministry_members` row + `user_roles` row (email + role="member" + ministry_id)
5. Member logs into Ministries site → sees their groups

---

## New Backend Endpoints (auth/member)

```
POST   /api/auth/member/login          — Verify Google token, check user_roles, issue JWT
GET    /api/auth/member/me             — Current user + their roles
GET    /api/member/ministries          — Ministries where user is leader or member
GET    /api/member/ministries/:id      — Ministry detail (if user has access)
POST   /api/member/ministries/:id/members     — Leader adds a member
GET    /api/member/ministries/:id/events       — Events for a ministry
POST   /api/member/ministries/:id/events       — Leader creates event
POST   /api/member/events/:id/attendance       — Leader records attendance
GET    /api/member/dashboard/week      — This week's events across user's ministries
```

Auth: JWT-based (not session/cookie like admin). Token issued on Google login, sent as `Authorization: Bearer <token>`.

---

## New Frontend: `ministries-frontend/`

Separate SvelteKit app in the same repo:

```
parishhub/
├── backend/              # Shared API
├── frontend/             # ParishHub admin (existing)
├── ministries-frontend/  # NEW — member-facing
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +page.svelte          # Landing / login
│   │   │   ├── dashboard/+page.svelte # Member dashboard (this week's events)
│   │   │   ├── groups/+page.svelte    # My groups list
│   │   │   ├── groups/[id]/+page.svelte # Group detail (members, events)
│   │   │   └── login/+page.svelte     # Google sign-in
│   │   ├── lib/
│   │   │   ├── api.ts                 # Member API client
│   │   │   ├── stores/                # Group, event, dashboard stores
│   │   │   └── components/            # EventCard, MemberList, etc.
│   │   └── hooks.server.ts            # JWT verification
│   ├── .env
│   └── package.json
```

### Dev ports
- ParishHub admin: `localhost:5173`
- Ministries frontend: `localhost:5174`
- API: `localhost:8000`

### Production
- ParishHub admin: `parishhub.com`
- Ministries: `ministries.parishhub.com` (subdomain via Cloudflare)
- API: `api.parishhub.com` (or same origin with path-based routing)

---

## What Changes in ParishHub Admin

Minimal changes — just remove the ministries frontend pages that were just added:

1. **Remove** `frontend/src/routes/ministries/` (list, new, detail pages)
2. **Remove** `frontend/src/lib/stores/ministries.ts`
3. **Keep** ministries management in admin but as a simpler admin-only section:
   - `/admin/ministries` — list + create ministries, assign leaders
   - Only accessible to priests/admins
4. **Keep** `frontend/src/lib/api.ts` ministry types (used by admin pages)
5. **Update** Nav.svelte — change "Ministries" link to `/admin/ministries`

The admin ministries page becomes a lightweight CRUD for setting up ministries and assigning leaders. No member-facing features.

---

## Implementation Order

### Phase 1: Backend — Member Auth & Endpoints
1. Add JWT token generation/validation to backend
2. Create `/api/auth/member/*` endpoints
3. Create `/api/member/*` endpoints (read-only + leader write actions)
4. Add RBAC middleware — verify user has required role for each action

### Phase 2: Ministries Frontend — Scaffold
5. Scaffold `ministries-frontend/` SvelteKit app
6. Set up Google OAuth (Auth.js or custom JWT flow)
7. Create API client + stores
8. Build login page
9. Build dashboard (this week's events)
10. Build groups list + detail pages
11. Build member management (leader adds members)
12. Build event creation (leader creates events)

### Phase 3: ParishHub Admin — Simplify
13. Slim down admin ministries pages to admin-only CRUD
14. Update Nav.svelte

### Phase 4: Production
15. Docker Compose — add ministries-frontend service
16. Nginx — route `ministries.parishhub.com` to new frontend
17. Cloudflare — add subdomain DNS

---

## Open Questions

1. **Can a person be in multiple ministries?** — Yes, the schema already supports this via `ministry_members` junction table.

2. **Email invitations?** — When a leader adds a member, should we send an email saying "You've been added to [Ministry]. Sign in at ministries.parishhub.com"? Future phase — not in v1.

## Decisions

- **Leader permissions:** Only admins can assign leaders. Leaders cannot assign co-leaders.
- **Google OAuth:** Same client ID, multiple redirect URIs (one for each frontend + environment).
- **Member auth:** JWT-based (stateless, Bearer token).
