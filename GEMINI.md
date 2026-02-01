# Parish Database - Gemini AI Context

## 1. Project Overview
A comprehensive parish management system handling members, households, sacraments, and analytics.
**Operating Environment:** Linux (Ubuntu/Debian based), Dockerized.

## 2. Technology Stack & Key Versions
- **Frontend:** SvelteKit 2, TypeScript, Tailwind CSS, Auth.js, Chart.js.
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2, Alembic, Slowapi.
- **Database:** PostgreSQL 15+.
- **Testing:** Pytest (Backend), Vitest (Frontend).
- **Containerization:** Docker & Docker Compose.

## 3. Architecture & Patterns

### Backend (`backend/`)
Follows a layered architecture: `Router` -> `Service` -> `Model`.

*   **Models (`app/models/`):** SQLAlchemy declarative models.
    *   *Convention:* One file per domain (e.g., `person.py`, `sacrament.py`). Use `Mapped` and `mapped_column` for typing.
*   **Schemas (`app/schemas/`):** Pydantic v2 models for request/response validation.
    *   *Convention:* `XCreate`, `XUpdate`, `XResponse`. Configured with `from_attributes = True`.
*   **Services (`app/services/`):** Business logic and DB interactions.
    *   *Convention:* Class-based services (e.g., `PersonService`) with dependency injection for the DB session.
*   **Routers (`app/routers/`):** API endpoints.
    *   *Convention:* Grouped by domain. Use `APIRouter`. Depend on services.

### Frontend (`frontend/`)
SvelteKit application with centralized API handling.

*   **API Client (`src/lib/api.ts`):** **CRITICAL.** All API calls MUST go through this file.
    *   *Convention:* Define types (interfaces) and a domain-specific object (e.g., `personApi`, `sacramentApi`) exporting methods.
*   **Stores (`src/lib/stores/`):** Svelte stores for shared state (e.g., toast notifications, user session).
*   **Components (`src/lib/components/`):** Reusable UI components.
*   **Routes (`src/routes/`):** File-system based routing.

## 4. Development Workflows

### Adding a New Feature (e.g., "Deaths")
1.  **Backend Model:** Create `backend/app/models/new_feature.py`. Add relationships in existing models.
2.  **Backend Schema:** Create `backend/app/schemas/new_feature.py` with Pydantic models.
3.  **Backend Service:** Create `backend/app/services/new_feature.py` for logic.
4.  **Backend Router:** Create `backend/app/routers/new_feature.py`. Register in `main.py`.
5.  **Database Migration:** Run `alembic revision --autogenerate -m "Add new feature"` and `alembic upgrade head`.
6.  **Frontend API:** Update `frontend/src/lib/api.ts` with new types and API methods.
7.  **Frontend UI:** Create components in `src/lib/components/` and pages in `src/routes/`.

### Running Tests
*   **Backend:** `cd backend && pytest`
*   **Frontend:** `cd frontend && npm run test`

## 5. Key File Locations
| Context | File Path |
| :--- | :--- |
| **App Entry** | `backend/app/main.py` |
| **DB Config** | `backend/app/database.py` |
| **Migrations** | `backend/alembic/versions/` |
| **Frontend API** | `frontend/src/lib/api.ts` |
| **Main Layout** | `frontend/src/routes/+layout.svelte` |
| **Styles** | `frontend/src/app.css` (Tailwind) |

## 6. Common Commands
*   **Start Dev:** `docker-compose up -d`
*   **Rebuild:** `docker-compose up -d --build`
*   **Backend Shell:** `docker-compose exec backend bash`
*   **DB Shell:** `docker-compose exec db psql -U postgres parish`

## 7. Interaction Rules for Agents
*   **Read First:** Check `GEMINI.md` (this file) and `docs/plans/` before starting complex tasks.
*   **Consistency:** Match the coding style of `backend/app/services/person.py` and `frontend/src/lib/api.ts`.
*   **Safety:** Always verify database migrations before applying.