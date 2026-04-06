"""Admin CLI for Parish Database — Typer-based commands."""

import typer
from random import choice

from app.database import SessionLocal
from app.models.person import Person
from app.schemas.person import PersonCreate
from app.services.person import PersonService

app = typer.Typer(help="Parish Database admin CLI")


@app.command()
def stats() -> None:
    """Print dashboard statistics."""
    db = SessionLocal()
    try:
        person_count = db.query(Person).count()
        typer.echo(f"Total persons: {person_count}")
    finally:
        db.close()


@app.command()
def seed(n: int = 10) -> None:
    """Seed the database with sample persons for development."""
    db = SessionLocal()
    try:
        svc = PersonService(db)
        first_names = [
            "Alice",
            "Bob",
            "Carol",
            "David",
            "Eve",
            "Frank",
            "Grace",
            "Henry",
        ]
        last_names = [
            "Smith",
            "Jones",
            "Brown",
            "Taylor",
            "Wilson",
            "Thomas",
            "Lee",
            "Clark",
        ]
        for _ in range(n):
            data = PersonCreate(
                first_name=choice(first_names),
                last_name=choice(last_names),
            )
            svc.create(data)
        typer.echo(f"Seeded {n} persons.")
    finally:
        db.close()


if __name__ == "__main__":
    app()
