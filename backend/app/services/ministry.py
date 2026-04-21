"""Service layer for Ministry operations (DIP compliant)."""

from datetime import date
import logging
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ministry import Ministry, MinistryEvent, MinistryMember, UserRole
from app.models.person import Person
from app.repositories.ministry import (
    FakeMinistryRepository,
    MinistryRepository,
    SqlAlchemyMinistryRepository,
)
from app.schemas.ministry import (
    AttendanceBatchCreate,
    MinistryCreate,
    MinistryEventCreate,
    MinistryEventUpdate,
    MinistryMemberCreate,
    MinistryMemberUpdate,
    MinistryUpdate,
)

from fastapi import Depends

logger = logging.getLogger("parish.ministry")


class MinistryValidationError(Exception):
    """Exception raised for ministry validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class MinistryService:
    """Service for Ministry CRUD with domain validation.

    All persistence is delegated to MinistryRepository (DIP).
    Direct DB access retained ONLY for cross-entity validation
    (e.g. checking Person exists before adding to ministry).
    """

    def __init__(self, repo: MinistryRepository, db: Session):
        self.repo = repo
        self.db = db

    # -----------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------
    def _validate_person_exists(self, person_id: int) -> Person:
        """Verify person exists before adding to ministry."""
        person = self.db.get(Person, person_id)
        if person is None:
            raise MinistryValidationError(
                f"Person with id {person_id} not found"
            )
        return person

    def _validate_not_duplicate_member(
        self, ministry_id: int, person_id: int
    ) -> None:
        """Reject if person is already in this ministry."""
        existing = self.repo.get_person_ministries(person_id)
        for m in existing:
            if m.ministry_id == ministry_id:
                raise MinistryValidationError(
                    "This person is already a member of this ministry"
                )

    # -----------------------------------------------------------------
    # Ministry CRUD
    # -----------------------------------------------------------------
    def create_ministry(self, data: MinistryCreate) -> Ministry:
        ministry = self.repo.create(data)
        logger.info("ministry_created: ministry_id=%s name=%s", ministry.id, ministry.name)

        # Auto-add leader as member
        if data.leader_id:
            self._validate_person_exists(data.leader_id)
            member_data = MinistryMemberCreate(
                ministry_id=ministry.id,
                person_id=data.leader_id,
                role="leader",
                joined_date=date.today(),
            )
            self.repo.add_member(member_data)
            logger.info(
                "ministry_leader_added: ministry_id=%s person_id=%s",
                ministry.id,
                data.leader_id,
            )

        return ministry

    def get_ministry(self, ministry_id: int) -> Optional[Ministry]:
        return self.repo.get_by_id(ministry_id)

    def get_ministry_detail(self, ministry_id: int) -> Optional[Ministry]:
        return self.repo.get_by_id_with_members(ministry_id)

    def list_ministries(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Ministry], int]:
        return self.repo.get_list(
            page, per_page, search, is_active, sort_by, sort_order
        )

    def update_ministry(
        self, ministry_id: int, data: MinistryUpdate
    ) -> Optional[Ministry]:
        ministry = self.repo.update(ministry_id, data)
        if ministry:
            logger.info(
                "ministry_updated: ministry_id=%s fields=%s",
                ministry_id,
                list(data.model_dump(exclude_unset=True).keys()),
            )
        return ministry

    def delete_ministry(self, ministry_id: int) -> bool:
        ministry = self.repo.get_by_id(ministry_id)
        if ministry is None:
            return False

        members = self.repo.get_members(ministry_id)
        events = self.repo.get_events(ministry_id)
        if members or events:
            # Soft delete
            self.repo.update(ministry_id, MinistryUpdate(is_active=False))
            logger.info("ministry_deleted: ministry_id=%s soft=%s", ministry_id, True)
            return True

        # Hard delete if empty
        result = self.repo.delete(ministry_id)
        if result:
            logger.info("ministry_deleted: ministry_id=%s soft=%s", ministry_id, False)
        return result

    # -----------------------------------------------------------------
    # Members
    # -----------------------------------------------------------------
    def add_member(self, data: MinistryMemberCreate) -> MinistryMember:
        self._validate_person_exists(data.person_id)
        self._validate_not_duplicate_member(data.ministry_id, data.person_id)

        # Auto-assign role: first person = leader, everyone after = co-leader
        existing_members = self.repo.get_members(data.ministry_id)
        has_leader = any(m.role == "leader" for m in existing_members)
        if has_leader:
            data.role = "co-leader"
        else:
            data.role = "leader"

        member = self.repo.add_member(data)
        logger.info(
            "ministry_member_added: ministry_id=%s person_id=%s",
            data.ministry_id,
            data.person_id,
        )
        return member

    def update_member(
        self, ministry_id: int, person_id: int, data: MinistryMemberUpdate
    ) -> Optional[MinistryMember]:
        return self.repo.update_member(ministry_id, person_id, data)

    def remove_member(self, ministry_id: int, person_id: int) -> bool:
        result = self.repo.remove_member(ministry_id, person_id)
        if result:
            logger.info(
                "ministry_member_removed: ministry_id=%s person_id=%s",
                ministry_id,
                person_id,
            )
        return result

    def get_person_ministries(self, person_id: int) -> list[MinistryMember]:
        return self.repo.get_person_ministries(person_id)

    # -----------------------------------------------------------------
    # Events
    # -----------------------------------------------------------------
    def create_event(self, data: MinistryEventCreate) -> MinistryEvent:
        event = self.repo.create_event(data)
        logger.info("ministry_event_created: event_id=%s title=%s", event.id, event.title)
        return event

    def list_events(
        self,
        ministry_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[MinistryEvent]:
        return self.repo.get_events(ministry_id, date_from, date_to)

    def update_event(
        self, event_id: int, data: MinistryEventUpdate
    ) -> Optional[MinistryEvent]:
        return self.repo.update_event(event_id, data)

    def delete_event(self, event_id: int) -> bool:
        result = self.repo.delete_event(event_id)
        if result:
            logger.info("ministry_event_deleted: event_id=%s", event_id)
        return result

    # -----------------------------------------------------------------
    # Cross-ministry events (calendar)
    # -----------------------------------------------------------------
    def list_all_events(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        ministry_id: Optional[int] = None,
    ) -> list[tuple[MinistryEvent, str]]:
        return self.repo.get_all_events(date_from, date_to, ministry_id)

    # -----------------------------------------------------------------
    # Attendance
    # -----------------------------------------------------------------
    def record_attendance(
        self, event_id: int, person_ids: list[int]
    ) -> int:
        event = self.repo.get_event_by_id(event_id)
        if event is None:
            raise MinistryValidationError(f"Event with id {event_id} not found")

        # Validate all persons exist
        for pid in person_ids:
            self._validate_person_exists(pid)

        count = self.repo.record_attendance(event_id, person_ids)
        logger.info("ministry_attendance_recorded: event_id=%s count=%s", event_id, count)
        return count

    def get_attendance(self, event_id: int) -> list:
        return self.repo.get_attendance(event_id)

    # -----------------------------------------------------------------
    # Statistics
    # -----------------------------------------------------------------
    def get_statistics(self) -> dict[str, Any]:
        return self.repo.get_statistics()


def get_ministry_service(db: Session = Depends(get_db)) -> MinistryService:
    """FastAPI dependency that returns a MinistryService with SQLAlchemy repo."""
    return MinistryService(SqlAlchemyMinistryRepository(db), db)
