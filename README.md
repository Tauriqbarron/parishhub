# Parish Database

A comprehensive web-based application designed for parishes to manage member information, families, sacraments, and attendance records. This solution provides tools for administrative staff to maintain accurate records and generate insightful analytics about their community.

## 🚀 Features

- **Member Management**: Detailed profiles for individual parishioners including contact info, dates of birth, and gender.
- **Household Tracking**: Group members into households with defined roles (Head of Household, Spouse, Child, etc.).
- **Sacramental Registry**: Record and track sacraments (Baptism, First Communion, Confirmation, Marriage, etc.) for each member.
- **Family Relationships**: Dynamic linking of family members (parents, children, siblings) to understand community connections.
- **Mass Attendance**: Track attendance numbers for different mass times and services.
- **Analytics & Reporting**:
    - Population growth trends.
    - Mass attendance statistics.
    - Birth statistics and demographics.
- **Public Registration**: Configurable public-facing forms for new family registration.
- **Secure Authentication**: Protected API endpoints requiring authentication.

## 🛠️ Tech Stack

### Frontend
- **Framework**: [SvelteKit 2](https://kit.svelte.dev/)
- **Language**: TypeScript
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Authentication**: Auth.js (@auth/sveltekit)
- **Visualization**: Chart.js for analytics dashboards
- **Testing**: Vitest, Testing Library

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Async)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Analysis & Rate Limiting**: Slowapi
- **Testing**: Pytest, HTTPX

### Infrastructure & Database
- **Database**: PostgreSQL
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- **OR** for local development:
    - Node.js 18+
    - Python 3.11+
    - PostgreSQL 15+

## ⚡ Getting Started (Docker)

The easiest way to run the application is using Docker Compose.

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd parish-database
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```
   
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Docs (Swagger)**: http://localhost:8000/docs
   - **Database**: localhost:5432

## 💻 Local Development Setup

If you prefer to run services individually for development:

### 1. Database Setup
Ensure you have a PostgreSQL database running. You can use the docker-compose file to just run the db:
```bash
docker-compose up -d db
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment example
cp ../.env.example .env
# Edit .env to match your local database credentials if needed

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm run test  # Run unit tests
npm run check # Run TypeScript check
```

## 📁 Project Structure

```
parish-database/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── models/        # SQLAlchemy Database Models
│   │   ├── routers/       # API Endpoints (Controllers)
│   │   ├── schemas/       # Pydantic Schemas (Data Transfer Objects)
│   │   └── services/      # Business Logic
│   ├── tests/             # Pytest tests
│   └── alembic/           # Database migrations
├── frontend/              # SvelteKit application
│   ├── src/
│   │   ├── lib/           # Components, stores, and utilities
│   │   └── routes/        # Application pages
│   └── static/            # Static assets
└── docker-compose.yml     # Container orchestration
```
