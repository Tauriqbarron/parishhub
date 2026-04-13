"""Tests for app.database.get_db generator."""

from sqlalchemy.orm import sessionmaker

from app.database import get_db


class TestGetDb:
    def test_yields_session(self, db_engine):
        """get_db() yields a usable SQLAlchemy Session."""
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        # Override module-level SessionLocal so get_db uses the test engine
        import app.database as db_module

        original = db_module.SessionLocal
        db_module.SessionLocal = TestSession
        try:
            gen = get_db()
            session = next(gen)
            assert session is not None
            # Session should be usable — execute a trivial query
            session.execute(
                db_module.Base.metadata.bind.dialect.name.__class__.__name__
                if False
                else __import__("sqlalchemy").text("SELECT 1")
            )
            # Clean up
            try:
                next(gen)
            except StopIteration:
                pass
        finally:
            db_module.SessionLocal = original

    def test_closes_session_after_generator_exhausted(self, db_engine):
        """After the generator finishes, the session is closed."""
        import app.database as db_module

        original = db_module.SessionLocal
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        db_module.SessionLocal = TestSession
        try:
            gen = get_db()
            session = next(gen)
            # Track whether close() was called
            close_called = False
            original_close = session.close

            def tracked_close():
                nonlocal close_called
                close_called = True
                original_close()

            session.close = tracked_close
            # Exhaust the generator (triggers finally → close)
            try:
                next(gen)
            except StopIteration:
                pass
            assert close_called is True
        finally:
            db_module.SessionLocal = original

    def test_generator_protocol(self, db_engine):
        """get_db is a generator that yields exactly once."""
        import app.database as db_module

        original = db_module.SessionLocal
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        db_module.SessionLocal = TestSession
        try:
            gen = get_db()
            # First next yields a session
            session = next(gen)
            assert session is not None
            # Second next raises StopIteration (generator is done)
            import pytest

            with pytest.raises(StopIteration):
                next(gen)
        finally:
            db_module.SessionLocal = original
