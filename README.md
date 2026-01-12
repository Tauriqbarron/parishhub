# Parish Database

A web based application for storing and searching information about parish members and families.

## Tech Stack

- **Frontend**: SvelteKit with TypeScript, Tailwind CSS
- **Backend**: FastAPI with SQLAlchemy
- **Database**: PostgreSQL

## Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose

## Getting Started

### 1. Start the Database

```bash
docker-compose up -d
```

This starts PostgreSQL on `localhost:5432`.

### 2. Set Up the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env

# Run the backend
uvicorn app.main:app --reload
```

The API runs on `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### 3. Set Up the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

The frontend runs on `http://localhost:5173`.

## Project Structure

```
parish-database/
├── frontend/                 # SvelteKit application
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/   # Reusable UI components
│   │   │   ├── stores/       # Svelte stores
│   │   │   └── api.ts        # API client
│   │   ├── routes/           # SvelteKit routes
│   │   └── app.html
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.ts
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── main.py           # FastAPI app entry
│   │   ├── config.py         # Settings management
│   │   ├── database.py       # SQLAlchemy setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API route handlers
│   │   └── services/         # Business logic
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── alembic.ini
├── docker-compose.yml        # Local development
└── .env.example
```

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /docs` - Swagger API documentation
