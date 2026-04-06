"""Unit tests for AuditService."""

from datetime import date

from sqlalchemy.orm import Session

from app.services.audit import AuditService


class TestAuditCreate:
    def test_log_create_all_fields(self, db_session: Session):
        svc = AuditService(db_session)
        entry = svc.log_create(
            resource_type="person",
            resource_id=42,
            new_values={"first_name": "John", "last_name": "Smith"},
            user_email="admin@test.com",
            user_ip="10.0.0.1",
            description="Created person via API",
        )
        db_session.commit()

        assert entry.id is not None
        assert entry.action == "CREATE"
        assert entry.resource_type == "person"
        assert entry.resource_id == 42
        assert entry.user_email == "admin@test.com"
        assert entry.user_ip == "10.0.0.1"
        assert entry.old_values is None
        assert entry.new_values == {"first_name": "John", "last_name": "Smith"}
        assert entry.description == "Created person via API"

    def test_log_create_minimal(self, db_session: Session):
        svc = AuditService(db_session)
        entry = svc.log_create(
            resource_type="death",
            resource_id=1,
            new_values={"date_of_death": "2024-01-15"},
        )
        db_session.commit()

        assert entry.user_email is None
        assert entry.user_ip is None
        assert entry.description is None


class TestAuditUpdate:
    def test_log_update(self, db_session: Session):
        svc = AuditService(db_session)
        entry = svc.log_update(
            resource_type="person",
            resource_id=42,
            old_values={"first_name": "John", "last_name": "Smith"},
            new_values={"first_name": "John", "last_name": "Doe"},
            user_email="admin@test.com",
            user_ip="10.0.0.1",
        )
        db_session.commit()

        assert entry.action == "UPDATE"
        assert entry.old_values == {"first_name": "John", "last_name": "Smith"}
        assert entry.new_values == {"first_name": "John", "last_name": "Doe"}

    def test_log_update_full_details(self, db_session: Session):
        svc = AuditService(db_session)
        entry = svc.log_update(
            resource_type="sacrament",
            resource_id=7,
            old_values={"type": "baptism", "date_performed": "2020-01-01"},
            new_values={"type": "baptism", "date_performed": "2020-02-01"},
            user_email="admin@test.com",
            user_ip="192.168.1.1",
            description="Corrected baptism date",
        )
        db_session.commit()

        assert entry.resource_type == "sacrament"
        assert entry.description == "Corrected baptism date"
        assert entry.old_values["date_performed"] == "2020-01-01"
        assert entry.new_values["date_performed"] == "2020-02-01"


class TestAuditDelete:
    def test_log_delete(self, db_session: Session):
        svc = AuditService(db_session)
        entry = svc.log_delete(
            resource_type="person",
            resource_id=42,
            old_values={"first_name": "John", "last_name": "Smith"},
            user_email="admin@test.com",
            user_ip="10.0.0.1",
            description="Deleted inactive person",
        )
        db_session.commit()

        assert entry.action == "DELETE"
        assert entry.old_values == {"first_name": "John", "last_name": "Smith"}
        assert entry.new_values is None
        assert entry.description == "Deleted inactive person"


class TestAuditQueries:
    def test_get_by_resource(self, db_session: Session):
        svc = AuditService(db_session)
        svc.log_create(resource_type="person", resource_id=42, new_values={"name": "A"})
        svc.log_update(
            resource_type="person",
            resource_id=42,
            old_values={"name": "A"},
            new_values={"name": "B"},
        )
        svc.log_delete(resource_type="person", resource_id=42, old_values={"name": "B"})
        # Different resource
        svc.log_create(resource_type="person", resource_id=99, new_values={"name": "X"})
        db_session.commit()

        entries = svc.get_by_resource("person", 42)
        assert len(entries) == 3
        assert all(e.resource_id == 42 for e in entries)
        assert entries[0].action == "DELETE"  # Most recent first

    def test_get_by_user(self, db_session: Session):
        svc = AuditService(db_session)
        svc.log_create(
            resource_type="person",
            resource_id=1,
            new_values={},
            user_email="admin@test.com",
        )
        svc.log_update(
            resource_type="person",
            resource_id=2,
            old_values={},
            new_values={},
            user_email="admin@test.com",
        )
        svc.log_create(
            resource_type="person",
            resource_id=3,
            new_values={},
            user_email="other@test.com",
        )
        db_session.commit()

        entries = svc.get_by_user("admin@test.com")
        assert len(entries) == 2
        assert all(e.user_email == "admin@test.com" for e in entries)

    def test_get_recent_orders_by_timestamp(self, db_session: Session):
        svc = AuditService(db_session)
        for i in range(5):
            svc.log_create(resource_type="person", resource_id=i, new_values={})
        db_session.commit()

        entries = svc.get_recent(limit=3)
        assert len(entries) == 3
        # Most recent first
        assert entries[0].resource_id >= entries[1].resource_id
        assert entries[1].resource_id >= entries[2].resource_id

    def test_get_by_date_range(self, db_session: Session):
        svc = AuditService(db_session)
        svc.log_create(resource_type="person", resource_id=1, new_values={})
        db_session.commit()

        start = date(2020, 1, 1)
        end = date(2026, 12, 31)
        entries = svc.get_by_date_range(start, end)
        assert len(entries) >= 1

    def test_get_recent_returns_ordered_results(self, db_session: Session):
        svc = AuditService(db_session)
        for i in range(10):
            svc.log_create(
                resource_type="person",
                resource_id=i,
                new_values={},
            )
        db_session.commit()

        entries = svc.get_recent(limit=5)
        assert len(entries) == 5
        # Verify descending order by timestamp
        for i in range(len(entries) - 1):
            assert entries[i].timestamp >= entries[i + 1].timestamp


class TestAuditTimestamp:
    def test_timestamp_is_set_on_create(self, db_session: Session):
        svc = AuditService(db_session)
        entry = svc.log_create(resource_type="person", resource_id=1, new_values={})
        db_session.commit()

        assert entry.timestamp is not None
