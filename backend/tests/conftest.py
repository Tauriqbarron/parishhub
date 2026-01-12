"""Pytest fixtures for testing."""

from datetime import date
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import JSON, create_engine, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.person import Gender, Person


@pytest.fixture(scope="function")
def db_engine():
    """Create an in-memory SQLite database engine for testing."""
    # Replace JSONB with JSON for SQLite compatibility
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, JSONB):
                column.type = JSON()

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_person_data() -> dict:
    """Sample person data for creating test persons."""
    return {
        "first_name": "John",
        "last_name": "Smith",
    }


@pytest.fixture
def full_person_data() -> dict:
    """Full person data for creating test persons with all fields."""
    return {
        "first_name": "John",
        "middle_name": "Michael",
        "last_name": "Smith",
        "date_of_birth": "1985-03-15",
        "gender": "male",
        "email": "john.smith@email.com",
        "phone": "+64 21 123 4567",
        "address_line1": "123 Main Street",
        "city": "Auckland",
        "postal_code": "1010",
        "notes": "Joined parish in 2020",
    }


@pytest.fixture
def sample_person(db_session: Session) -> Person:
    """Create a sample person in the database."""
    person = Person(
        first_name="John",
        last_name="Smith",
        email="john.smith@test.com",
        gender=Gender.MALE,
        date_of_birth=date(1985, 3, 15),
    )
    db_session.add(person)
    db_session.commit()
    db_session.refresh(person)
    return person


@pytest.fixture
def multiple_persons(db_session: Session) -> list[Person]:
    """Create multiple persons in the database for pagination testing."""
    persons = [
        Person(first_name="Alice", last_name="Anderson", email="alice@test.com", gender=Gender.FEMALE),
        Person(first_name="Bob", last_name="Brown", email="bob@test.com", gender=Gender.MALE),
        Person(first_name="Carol", last_name="Chen", email="carol@test.com", gender=Gender.FEMALE),
        Person(first_name="David", last_name="Davis", email="david@test.com", gender=Gender.MALE),
        Person(first_name="Eve", last_name="Evans", email="eve@test.com", gender=Gender.FEMALE),
    ]
    for person in persons:
        db_session.add(person)
    db_session.commit()
    for person in persons:
        db_session.refresh(person)
    return persons
