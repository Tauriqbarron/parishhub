.PHONY: seed stats migrate shell backend-run

seed:
	cd backend && python -m app.cli seed

stats:
	cd backend && python -m app.cli stats

migrate:
	cd backend && alembic upgrade head

migrate-head:
	cd backend && alembic upgrade head

makemigration:
	cd backend && alembic revision --autogenerate -m "auto"

backend-run:
	cd backend && uvicorn app.main:app --reload --port 8000

shell:
	cd backend && python -c "from app.database import SessionLocal; db = SessionLocal(); print('DB session available. Use db.close() when done.')"

lint:
	cd backend && ruff check app/

format:
	cd backend && ruff check --fix app/ && ruff format app/

test:
	cd backend && pytest tests/ -v

test-cov:
	cd backend && pytest tests/ -v --cov=app --cov-report=term-missing
