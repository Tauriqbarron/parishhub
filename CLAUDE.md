# Parish Database - Efficiency & Context Guidelines

## 1. Interaction Limits (Token Saving)

- **NO CHAT:** Do not reply with conversational text. Output only tool uses or final confirmation.
- **NO SUMMARIES:** Do not summarize changes after editing.
- **COMPACT:** If listing files, list only relevant ones.
- **CONTEXT:** Do not read `node_modules`, `venv`, `package-lock.json`, `.svelte-kit`, or `__pycache__`.

## 2. Architecture & Workflow

**Stack:** SvelteKit (Frontend) + FastAPI (Backend) + PostgreSQL.

### Backend (FastAPI)

- **Pattern:** `Schemas` (Pydantic) -> `Models` (SQLAlchemy) -> `CRUD` -> `Router`.
- **Edit Order:** When adding features, define the Pydantic schema in `backend/app/schemas/` *first*.
- **Imports:** Use absolute imports from `app.` (e.g., `from app.schemas import ...`).

### Frontend (SvelteKit)

- **State:** Use Svelte stores in `src/lib/stores/` for global state.
- **API:** All fetch calls must go through `src/lib/api.ts`. Do not use `fetch` directly in components.
- **Styling:** Use Tailwind utility classes. Do not write custom CSS in `<style>` blocks unless necessary.

## 3. Background Task Behavior

- **Auto-Poll:** When running background tasks, poll for completion and report results immediately - do NOT wait for user to ask.
- **Task Tracking:** Store task IDs and check TaskOutput periodically until complete.
- **Immediate Reporting:** When a background task finishes, summarize results in the next response.

## 4. Test & Verification

- **Frontend:** Run `npm run check` only if editing TypeScript types.
- **Backend:** Do not restart the Docker container unless the issue explicitly requires database config changes.
- **Linting:** Assume code is linted; do not run linters unless asked.
