"""Repository layer for Ministry CRUD and queries (DIP compliant)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.ministry import (
    Ministry,
    MinistryEvent,
    MinistryEventAttendance,
    MinistryMember,
    UserRole,
)
from app.models.person import Person
from app.schemas.ministry import (
    AttendanceBatchCreate,
    MinistryCreate,
    MinistryEventCreate,
    MinistryEventUpdate,
    MinistryMemberCreate,
    MinistryMemberUpdate,
    MinistryUpdate,
)


class MinistryRepository(ABC):
    """Abstract repository for ministry persistence operations."""

    # --- Ministry CRUD ---
    @abstractmethod
    def create(self, data: MinistryCreate) -> Ministry: ...

    @abstractmethod
    def get_by_id(self, ministry_id: int) -> Optional[Ministry]: ...

    @abstractmethod
    def get_by_id_with_members(self, ministry_id: int) -> Optional[Ministry]: ...

    @abstractmethod
    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Ministry], int]: ...

    @abstractmethod
    def update(self, ministry_id: int, data: MinistryUpdate) -> Optional[Ministry]: ...

    @abstractmethod
    def delete(self, ministry_id: int) -> bool: ...

    # --- Members ---
    @abstractmethod
    def add_member(self, data: MinistryMemberCreate) -> MinistryMember: ...

    @abstractmethod
    def get_members(self, ministry_id: int) -> list[MinistryMember]: ...

    @abstractmethod
    def update_member(
        self, ministry_id: int, person_id: int, data: MinistryMemberUpdate
    ) -> Optional[MinistryMember]: ...

    @abstractmethod
    def remove_member(self, ministry_id: int, person_id: int) -> bool: ...

    @abstractmethod
    def get_person_ministries(self, person_id: int) -> list[MinistryMember]: ...

    # --- Events ---
    @abstractmethod
    def create_event(self, data: MinistryEventCreate) -> MinistryEvent: ...

    @abstractmethod
    def get_events(
        self,
        ministry_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[MinistryEvent]: ...

    @abstractmethod
    def get_event_by_id(self, event_id: int) -> Optional[MinistryEvent]: ...

    @abstractmethod
    def update_event(
        self, event_id: int, data: MinistryEventUpdate
    ) -> Optional[MinistryEvent]: ...

    @abstractmethod
    def delete_event(self, event_id: int) -> bool: ...

    # --- Attendance ---
    @abstractmethod
    def record_attendance(self, event_id: int, person_ids: list[int]) -> int: ...

    @abstractmethod
    def get_attendance(self, event_id: int) -> list[MinistryEventAttendance]: ...

    # --- RBAC ---
    @abstractmethod
    def get_user_roles(self, email: str) -> list[UserRole]: ...

    @abstractmethod
    def get_user_role_in_ministry(
        self, email: str, ministry_id: int
    ) -> Optional[UserRole]: ...

    # --- Cross-ministry events (for calendar view) ---
    @abstractmethod
    def get_all_events(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        ministry_id: Optional[int] = None,
    ) -> list[tuple[MinistryEvent, str]]: ...

    # --- Statistics ---
    @abstractmethod
    def get_statistics(self) -> dict[str, Any]: ...


class SqlAlchemyMinistryRepository(MinistryRepository):
    """SQLAlchemy implementation of MinistryRepository."""

    def __init__(self, db: Session):
        self.db = db

    # --- Ministry CRUD ---
    def create(self, data: MinistryCreate) -> Ministry:
        ministry = Ministry(**data.model_dump())
        self.db.add(ministry)
        self.db.flush()
        self.db.commit()
        self.db.refresh(ministry)
        return ministry

    def get_by_id(self, ministry_id: int) -> Optional[Ministry]:
        return self.db.get(Ministry, ministry_id)

    def get_by_id_with_members(self, ministry_id: int) -> Optional[Ministry]:
        stmt = (
            select(Ministry)
            .options(
                selectinload(Ministry.members).selectinload(MinistryMember.person),
                selectinload(Ministry.events),
                selectinload(Ministry.leader),
            )
            .where(Ministry.id == ministry_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Ministry], int]:
        stmt = select(Ministry)
        count_stmt = select(func.count()).select_from(Ministry)

        if search:
            stmt = stmt.where(Ministry.name.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(Ministry.name.ilike(f"%{search}%"))
        if is_active is not None:
            stmt = stmt.where(Ministry.is_active == is_active)
            count_stmt = count_stmt.where(Ministry.is_active == is_active)

        column = getattr(Ministry, sort_by, Ministry.name)
        if sort_order.lower() == "desc":
            column = column.desc()
        stmt = stmt.order_by(column)

        total = self.db.execute(count_stmt).scalar() or 0
        offset = (page - 1) * per_page
        items = list(
            self.db.execute(stmt.offset(offset).limit(per_page)).scalars().all()
        )
        return items, total

    def update(self, ministry_id: int, data: MinistryUpdate) -> Optional[Ministry]:
        ministry = self.get_by_id(ministry_id)
        if ministry is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ministry, field, value)
        self.db.commit()
        self.db.refresh(ministry)
        return ministry

    def delete(self, ministry_id: int) -> bool:
        ministry = self.get_by_id(ministry_id)
        if ministry is None:
            return False
        self.db.delete(ministry)
        self.db.commit()
        return True

    # --- Members ---
    def add_member(self, data: MinistryMemberCreate) -> MinistryMember:
        member = MinistryMember(**data.model_dump())
        self.db.add(member)
        self.db.flush()
        self.db.commit()
        self.db.refresh(member)
        return member

    def get_members(self, ministry_id: int) -> list[MinistryMember]:
        stmt = (
            select(MinistryMember)
            .options(selectinload(MinistryMember.person))
            .where(MinistryMember.ministry_id == ministry_id)
            .order_by(MinistryMember.role, MinistryMember.joined_date)
        )
        return list(self.db.execute(stmt).scalars().all())

    def update_member(
        self, ministry_id: int, person_id: int, data: MinistryMemberUpdate
    ) -> Optional[MinistryMember]:
        stmt = select(MinistryMember).where(
            MinistryMember.ministry_id == ministry_id,
            MinistryMember.person_id == person_id,
        )
        member = self.db.execute(stmt).scalar_one_or_none()
        if member is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(member, field, value)
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_member(self, ministry_id: int, person_id: int) -> bool:
        stmt = select(MinistryMember).where(
            MinistryMember.ministry_id == ministry_id,
            MinistryMember.person_id == person_id,
        )
        member = self.db.execute(stmt).scalar_one_or_none()
        if member is None:
            return False
        self.db.delete(member)
        self.db.commit()
        return True

    def get_person_ministries(self, person_id: int) -> list[MinistryMember]:
        stmt = (
            select(MinistryMember)
            .options(selectinload(MinistryMember.ministry))
            .where(MinistryMember.person_id == person_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    # --- Events ---
    def create_event(self, data: MinistryEventCreate) -> MinistryEvent:
        event = MinistryEvent(**data.model_dump())
        self.db.add(event)
        self.db.flush()
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_events(
        self,
        ministry_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[MinistryEvent]:
        stmt = (
            select(MinistryEvent)
            .where(MinistryEvent.ministry_id == ministry_id)
            .order_by(MinistryEvent.event_date.desc())
        )
        if date_from:
            stmt = stmt.where(MinistryEvent.event_date >= date_from)
        if date_to:
            stmt = stmt.where(MinistryEvent.event_date <= date_to)
        return list(self.db.execute(stmt).scalars().all())

    def get_event_by_id(self, event_id: int) -> Optional[MinistryEvent]:
        return self.db.get(MinistryEvent, event_id)

    def update_event(
        self, event_id: int, data: MinistryEventUpdate
    ) -> Optional[MinistryEvent]:
        event = self.get_event_by_id(event_id)
        if event is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(event, field, value)
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete_event(self, event_id: int) -> bool:
        event = self.get_event_by_id(event_id)
        if event is None:
            return False
        self.db.delete(event)
        self.db.commit()
        return True

    # --- Attendance ---
    def record_attendance(self, event_id: int, person_ids: list[int]) -> int:
        count = 0
        for person_id in person_ids:
            existing = self.db.execute(
                select(MinistryEventAttendance).where(
                    MinistryEventAttendance.event_id == event_id,
                    MinistryEventAttendance.person_id == person_id,
                )
            ).scalar_one_or_none()
            if existing is None:
                record = MinistryEventAttendance(
                    event_id=event_id, person_id=person_id, attended=True
                )
                self.db.add(record)
                count += 1
        self.db.flush()
        self.db.commit()
        return count

    def get_attendance(self, event_id: int) -> list[MinistryEventAttendance]:
        stmt = (
            select(MinistryEventAttendance)
            .options(selectinload(MinistryEventAttendance.person))
            .where(MinistryEventAttendance.event_id == event_id)
        )
        return list(self.db.execute(stmt).scalars().all())

    # --- RBAC ---
    def get_user_roles(self, email: str) -> list[UserRole]:
        stmt = select(UserRole).where(UserRole.user_email == email)
        return list(self.db.execute(stmt).scalars().all())

    def get_user_role_in_ministry(
        self, email: str, ministry_id: int
    ) -> Optional[UserRole]:
        stmt = select(UserRole).where(
            UserRole.user_email == email,
            UserRole.ministry_id == ministry_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # --- Cross-ministry events (for calendar view) ---
    def get_all_events(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        ministry_id: Optional[int] = None,
    ) -> list[tuple[MinistryEvent, str]]:
        stmt = (
            select(MinistryEvent, Ministry.name)
            .join(Ministry, MinistryEvent.ministry_id == Ministry.id)
            .where(
                Ministry.is_active.is_(True),
                MinistryEvent.is_cancelled.is_(False),
            )
            .order_by(MinistryEvent.event_date)
        )
        if date_from:
            stmt = stmt.where(MinistryEvent.event_date >= date_from)
        if date_to:
            stmt = stmt.where(MinistryEvent.event_date <= date_to)
        if ministry_id:
            stmt = stmt.where(MinistryEvent.ministry_id == ministry_id)
        rows = self.db.execute(stmt).all()
        return [(event, ministry_name) for event, ministry_name in rows]

    # --- Statistics ---
    def get_statistics(self) -> dict[str, Any]:
        total = self.db.execute(
            select(func.count()).select_from(Ministry)
        ).scalar() or 0
        active = self.db.execute(
            select(func.count()).select_from(Ministry).where(Ministry.is_active.is_(True))
        ).scalar() or 0
        total_members = self.db.execute(
            select(func.count()).select_from(MinistryMember)
        ).scalar() or 0
        total_events = self.db.execute(
            select(func.count()).select_from(MinistryEvent)
        ).scalar() or 0
        return {
            "total_ministries": total,
            "active_ministries": active,
            "total_members": total_members,
            "total_events": total_events,
        }


class FakeMinistryRepository(MinistryRepository):
    """In-memory fake for unit tests."""

    def __init__(self):
        self._ministries: dict[int, Ministry] = {}
        self._members: dict[int, MinistryMember] = {}
        self._events: dict[int, MinistryEvent] = {}
        self._attendance: dict[int, MinistryEventAttendance] = {}
        self._roles: dict[int, UserRole] = {}
        self._next_id = 1

    def _gen_id(self) -> int:
        id_ = self._next_id
        self._next_id += 1
        return id_

    # --- Ministry CRUD ---
    def create(self, data: MinistryCreate) -> Ministry:
        m = Ministry(id=self._gen_id(), **data.model_dump())
        self._ministries[m.id] = m
        return m

    def get_by_id(self, ministry_id: int) -> Optional[Ministry]:
        return self._ministries.get(ministry_id)

    def get_by_id_with_members(self, ministry_id: int) -> Optional[Ministry]:
        return self._ministries.get(ministry_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Ministry], int]:
        items = list(self._ministries.values())
        if search:
            items = [m for m in items if search.lower() in m.name.lower()]
        if is_active is not None:
            items = [m for m in items if m.is_active == is_active]
        items.sort(
            key=lambda m: getattr(m, sort_by, m.name),
            reverse=(sort_order == "desc"),
        )
        total = len(items)
        offset = (page - 1) * per_page
        return items[offset : offset + per_page], total

    def update(self, ministry_id: int, data: MinistryUpdate) -> Optional[Ministry]:
        m = self._ministries.get(ministry_id)
        if m is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(m, field, value)
        return m

    def delete(self, ministry_id: int) -> bool:
        if ministry_id not in self._ministries:
            return False
        del self._ministries[ministry_id]
        return True

    # --- Members ---
    def add_member(self, data: MinistryMemberCreate) -> MinistryMember:
        m = MinistryMember(id=self._gen_id(), **data.model_dump())
        self._members[m.id] = m
        return m

    def get_members(self, ministry_id: int) -> list[MinistryMember]:
        return [m for m in self._members.values() if m.ministry_id == ministry_id]

    def update_member(
        self, ministry_id: int, person_id: int, data: MinistryMemberUpdate
    ) -> Optional[MinistryMember]:
        for m in self._members.values():
            if m.ministry_id == ministry_id and m.person_id == person_id:
                for field, value in data.model_dump(exclude_unset=True).items():
                    setattr(m, field, value)
                return m
        return None

    def remove_member(self, ministry_id: int, person_id: int) -> bool:
        for mid, m in list(self._members.items()):
            if m.ministry_id == ministry_id and m.person_id == person_id:
                del self._members[mid]
                return True
        return False

    def get_person_ministries(self, person_id: int) -> list[MinistryMember]:
        return [m for m in self._members.values() if m.person_id == person_id]

    # --- Events ---
    def create_event(self, data: MinistryEventCreate) -> MinistryEvent:
        e = MinistryEvent(id=self._gen_id(), **data.model_dump())
        self._events[e.id] = e
        return e

    def get_events(
        self,
        ministry_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[MinistryEvent]:
        events = [e for e in self._events.values() if e.ministry_id == ministry_id]
        if date_from:
            events = [e for e in events if e.event_date >= date_from]
        if date_to:
            events = [e for e in events if e.event_date <= date_to]
        return events

    def get_event_by_id(self, event_id: int) -> Optional[MinistryEvent]:
        return self._events.get(event_id)

    def update_event(
        self, event_id: int, data: MinistryEventUpdate
    ) -> Optional[MinistryEvent]:
        e = self._events.get(event_id)
        if e is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(e, field, value)
        return e

    def delete_event(self, event_id: int) -> bool:
        if event_id not in self._events:
            return False
        del self._events[event_id]
        return True

    # --- Attendance ---
    def record_attendance(self, event_id: int, person_ids: list[int]) -> int:
        count = 0
        for pid in person_ids:
            key = (event_id, pid)
            if not any(
                a.event_id == event_id and a.person_id == pid
                for a in self._attendance.values()
            ):
                a = MinistryEventAttendance(
                    id=self._gen_id(), event_id=event_id, person_id=pid, attended=True
                )
                self._attendance[a.id] = a
                count += 1
        return count

    def get_attendance(self, event_id: int) -> list[MinistryEventAttendance]:
        return [a for a in self._attendance.values() if a.event_id == event_id]

    # --- RBAC ---
    def get_user_roles(self, email: str) -> list[UserRole]:
        return [r for r in self._roles.values() if r.user_email == email]

    def get_user_role_in_ministry(
        self, email: str, ministry_id: int
    ) -> Optional[UserRole]:
        for r in self._roles.values():
            if r.user_email == email and r.ministry_id == ministry_id:
                return r
        return None

    # --- Cross-ministry events (for calendar view) ---
    def get_all_events(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        ministry_id: Optional[int] = None,
    ) -> list[tuple[MinistryEvent, str]]:
        results = []
        for e in self._events.values():
            m = self._ministries.get(e.ministry_id)
            if not m or not m.is_active or e.is_cancelled:
                continue
            if date_from and e.event_date < date_from:
                continue
            if date_to and e.event_date > date_to:
                continue
            if ministry_id and e.ministry_id != ministry_id:
                continue
            results.append((e, m.name))
        results.sort(key=lambda x: x[0].event_date)
        return results

    # --- Statistics ---
    def get_statistics(self) -> dict[str, Any]:
        return {
            "total_ministries": len(self._ministries),
            "active_ministries": sum(
                1 for m in self._ministries.values() if m.is_active
            ),
            "total_members": len(self._members),
            "total_events": len(self._events),
        }
