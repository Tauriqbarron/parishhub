# Parish Database - Copilot Instructions

## 1. General Guidelines & Efficiency
- **NO CHAT:** Do not reply with conversational text or summaries unless explicitly asked. Output only tool uses or final confirmation.
- **COMPACT:** Listing files? List only relevant ones.
- **VETO CONTEXT:** Do not read `node_modules`, `venv`, `package-lock.json`, `.svelte-kit`, or `__pycache__`.
- **Background Tasks:** Poll for completion and report results immediately. Store task IDs and check periodically.

## 2. Architecture & Workflow
**Stack:** SvelteKit (Frontend) + FastAPI (Backend) + PostgreSQL.

### Backend (FastAPI + Python)
- **Framework:** FastAPI 0.100+
- **ORM:** SQLAlchemy 2.0 (async patterns)
- **Validation:** Pydantic v2
- **Database:** PostgreSQL
- **Pattern:** `Schemas` (Pydantic) -> `Models` (SQLAlchemy) -> `CRUD` -> `Router` -> `Services`.
- **Implementation Order:**
    1. **Schema First:** Define Pydantic models in `backend/app/schemas/`.
    2. **Model:** Define SQLAlchemy models in `backend/app/models/`.
    3. **CRUD:** Add database operations.
    4. **Router:** Create/update endpoint in `backend/app/routers/`.
- **Imports:** Use absolute imports from `app.` (e.g., `from app.schemas import ...`). Do NOT use relative imports (e.g., `from ..schemas`).

### Frontend (SvelteKit + TypeScript)
- **Framework:** SvelteKit 2.x
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS ONLY. Do not use `<style>` blocks for custom CSS.
- **State:** Use Svelte stores in `src/lib/stores/` for global state.
- **API:**
    - **CRITICAL:** ALL fetch calls must go through `src/lib/api.ts`.
    - **NEVER** use `fetch` directly in components.
    - Use specific clients: `personApi`, `householdApi`, `sacramentApi`, etc.

## 3. Test & Verification
- **Frontend:** Run `npm run check` only if editing TypeScript types.
- **Backend:** Do not restart Docker unless database config changes.
- **Linting:** Assume code is linted; do not run linters unless asked.

## 4. Role-Specific Instructions

### Feature Planning
- Analyze feature requests and ask clarifying questions first (Scope, Data, UI/UX, Business Rules).
- Create implementation plans broken into:
    - **Backend Tasks:** Schema changes, Model updates, API endpoints.
    - **Frontend Tasks:** Store updates, UI components, Page integration.

### Code Quality
- **Backend:** Ensure proper Pydantic/SQLAlchemy separation. Use dependency injection for DB sessions (`get_db`).
- **Frontend:** Ensure strict typing for all props and state. Use `aria-label` and roles for accessibility.
