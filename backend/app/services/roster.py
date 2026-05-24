"""Service layer for Roster operations."""

import calendar
from datetime import date, datetime, timedelta, timezone
import logging
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.person import Person
from app.models.roster import (
    PersonRosterRole,
    RosterAssignment,
    RosterInstance,
    RosterRole,
    RosterSwapRequest,
    RosterTemplate,
    RosterTemplateSlot,
)
from app.schemas.roster import (
    RosterRoleCreate,
    RosterRoleUpdate,
    RosterTemplateCreate,
    RosterTemplateUpdate,
)

logger = logging.getLogger("parish.roster")


class RosterValidationError(Exception):
    """Exception raised for roster validation errors."""

    def __init__(self, message: str, detail: Optional[dict] = None):
        self.message = message
        self.detail = detail or {}
        super().__init__(self.message)


class RosterService:
    """Service for all roster operations — roles, templates, instances, assignments, swaps."""

    def __init__(self, db: Session):
        self.db = db

    # -----------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------
    def _validate_person_exists(self, person_id: int) -> Person:
        person = self.db.get(Person, person_id)
        if person is None:
            raise RosterValidationError(f"Person with id {person_id} not found")
        return person

    def _validate_person_has_role(self, person_id: int, role_id: int) -> bool:
        """Check if person has a specific roster role."""
        exists = (
            self.db.query(PersonRosterRole)
            .filter(
                PersonRosterRole.person_id == person_id,
                PersonRosterRole.role_id == role_id,
            )
            .first()
        )
        return exists is not None

    def _validate_slot_capacity(self, instance_id: int, slot_id: int, max_persons: int) -> int:
        """Check slot not over capacity. Returns current count."""
        count = (
            self.db.query(RosterAssignment)
            .filter(
                RosterAssignment.instance_id == instance_id,
                RosterAssignment.slot_id == slot_id,
                RosterAssignment.person_id.isnot(None),  # exclude placeholder assignments
            )
            .count()
        )
        if count >= max_persons:
            raise RosterValidationError(
                f"Slot is at capacity ({count}/{max_persons})"
            )
        return count

    def _validate_status_transition(self, current: str, target: str) -> None:
        """Ensure valid assignment status transitions."""
        valid_transitions = {
            "pending": {"accepted", "declined", "cancelled"},
            "accepted": {"completed", "cancelled"},
            "declined": set(),  # terminal
            "completed": set(),  # terminal
            "cancelled": set(),  # terminal
        }
        allowed = valid_transitions.get(current, set())
        if target not in allowed:
            raise RosterValidationError(
                f"Cannot transition from '{current}' to '{target}'"
            )

    def _copy_assignments_from_previous(self, instance: RosterInstance) -> None:
        """Copy assignments from most recent completed instance for same template (keep_assignee)."""
        template = instance.template
        if not template.settings.get("keep_assignee"):
            return

        prev_instance = (
            self.db.query(RosterInstance)
            .filter(
                RosterInstance.template_id == instance.template_id,
                RosterInstance.status == "completed",
                RosterInstance.id != instance.id,
            )
            .order_by(RosterInstance.date.desc())
            .first()
        )
        if not prev_instance:
            return

        for prev_assignment in prev_instance.assignments:
            # Only copy accepted/completed assignments
            if prev_assignment.status in ("accepted", "completed"):
                new_asgn = RosterAssignment(
                    instance_id=instance.id,
                    slot_id=prev_assignment.slot_id,
                    person_id=prev_assignment.person_id,
                    status="pending",
                    assigned_at=datetime.now(timezone.utc),
                )
                self.db.add(new_asgn)
        self.db.flush()

    # -----------------------------------------------------------------
    # Role management
    # -----------------------------------------------------------------
    def create_role(self, data: RosterRoleCreate) -> RosterRole:
        role = RosterRole(name=data.name, description=data.description)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        logger.info("roster_role_created: role_id=%s name=%s", role.id, role.name)
        return role

    def list_roles(self) -> list[RosterRole]:
        return self.db.query(RosterRole).order_by(RosterRole.name).all()

    def get_role(self, role_id: int) -> RosterRole:
        role = self.db.get(RosterRole, role_id)
        if role is None:
            raise RosterValidationError(f"RosterRole {role_id} not found")
        return role

    def update_role(self, role_id: int, data: RosterRoleUpdate) -> RosterRole:
        role = self.get_role(role_id)
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        self.db.commit()
        self.db.refresh(role)
        logger.info("roster_role_updated: role_id=%s", role_id)
        return role

    def delete_role(self, role_id: int) -> bool:
        role = self.get_role(role_id)
        # Check if role is referenced by any template slots
        slot_count = (
            self.db.query(RosterTemplateSlot)
            .filter(RosterTemplateSlot.role_id == role_id)
            .count()
        )
        if slot_count > 0:
            raise RosterValidationError(
                f"Cannot delete role '{role.name}': referenced by {slot_count} template slot(s)"
            )
        self.db.delete(role)
        self.db.commit()
        logger.info("roster_role_deleted: role_id=%s", role_id)
        return True

    # -----------------------------------------------------------------
    # Person-Role assignments
    # -----------------------------------------------------------------
    def assign_role_to_person(
        self, person_id: int, role_id: int, assigned_by: Optional[int] = None
    ) -> PersonRosterRole:
        self._validate_person_exists(person_id)
        self.get_role(role_id)
        # Check for duplicate
        existing = (
            self.db.query(PersonRosterRole)
            .filter(
                PersonRosterRole.person_id == person_id,
                PersonRosterRole.role_id == role_id,
            )
            .first()
        )
        if existing:
            raise RosterValidationError("Person already has this role")
        prr = PersonRosterRole(
            person_id=person_id, role_id=role_id, assigned_by=assigned_by
        )
        self.db.add(prr)
        self.db.commit()
        self.db.refresh(prr)
        logger.info("person_role_assigned: person_id=%s role_id=%s", person_id, role_id)
        return prr

    def remove_role_from_person(self, person_id: int, role_id: int) -> bool:
        prr = (
            self.db.query(PersonRosterRole)
            .filter(
                PersonRosterRole.person_id == person_id,
                PersonRosterRole.role_id == role_id,
            )
            .first()
        )
        if prr is None:
            raise RosterValidationError("Person does not have this role")
        self.db.delete(prr)
        self.db.commit()
        logger.info("person_role_removed: person_id=%s role_id=%s", person_id, role_id)
        return True

    def get_person_roles(self, person_id: int) -> list[RosterRole]:
        return (
            self.db.query(RosterRole)
            .join(PersonRosterRole)
            .filter(PersonRosterRole.person_id == person_id)
            .order_by(RosterRole.name)
            .all()
        )

    # -----------------------------------------------------------------
    # Template management
    # -----------------------------------------------------------------
    def create_template(
        self, data: RosterTemplateCreate, created_by: Optional[int] = None
    ) -> RosterTemplate:
        template = RosterTemplate(
            name=data.name,
            description=data.description,
            ministry_id=data.ministry_id,
            mass_time_id=data.mass_time_id,
            event_id=data.event_id,
            recurrence_rule=data.recurrence_rule,
            recurrence_end=data.recurrence_end,
            settings=data.settings.model_dump() if data.settings else {},
            is_active=data.is_active,
            created_by=created_by,
        )
        self.db.add(template)
        self.db.flush()  # Get template.id

        for slot_data in data.slots:
            slot = RosterTemplateSlot(
                template_id=template.id,
                role_id=slot_data.role_id,
                label=slot_data.label,
                sort_order=slot_data.sort_order,
                min_persons=slot_data.min_persons,
                max_persons=slot_data.max_persons,
            )
            self.db.add(slot)

        self.db.commit()
        self.db.refresh(template)
        logger.info("roster_template_created: template_id=%s name=%s", template.id, template.name)
        return template

    def list_templates(
        self, ministry_id: Optional[int] = None, is_active: Optional[bool] = None,
        include_parish: bool = False,
    ) -> list[RosterTemplate]:
        query = self.db.query(RosterTemplate).options(
            joinedload(RosterTemplate.slots)
        )
        if ministry_id is not None:
            if include_parish:
                # Return templates for this ministry AND parish-wide templates
                from sqlalchemy import or_
                query = query.filter(or_(
                    RosterTemplate.ministry_id == ministry_id,
                    RosterTemplate.ministry_id.is_(None),
                ))
            else:
                query = query.filter(RosterTemplate.ministry_id == ministry_id)
        if is_active is not None:
            query = query.filter(RosterTemplate.is_active == is_active)
        return query.order_by(RosterTemplate.name).all()

    def get_template(self, template_id: int) -> RosterTemplate:
        template = (
            self.db.query(RosterTemplate)
            .options(
                joinedload(RosterTemplate.slots),
                joinedload(RosterTemplate.instances),
            )
            .filter(RosterTemplate.id == template_id)
            .first()
        )
        if template is None:
            raise RosterValidationError(f"RosterTemplate {template_id} not found")
        return template

    def update_template(
        self, template_id: int, data: RosterTemplateUpdate
    ) -> RosterTemplate:
        template = self.get_template(template_id)
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if key == "settings" and value is not None:
                # Already a dict from model_dump(exclude_unset=True) above
                setattr(template, key, value)
            elif key != "slots":
                setattr(template, key, value)
        self.db.commit()
        self.db.refresh(template)
        logger.info("roster_template_updated: template_id=%s", template_id)
        return template

    def delete_template(self, template_id: int) -> bool:
        template = self.get_template(template_id)
        self.db.delete(template)
        self.db.commit()
        logger.info("roster_template_deleted: template_id=%s", template_id)
        return True

    def duplicate_template(self, template_id: int) -> RosterTemplate:
        """Clone a template with '(copy)' suffix."""
        original = self.get_template(template_id)
        new_template = RosterTemplate(
            name=f"{original.name} (copy)",
            description=original.description,
            ministry_id=original.ministry_id,
            mass_time_id=original.mass_time_id,
            event_id=original.event_id,
            recurrence_rule=original.recurrence_rule,
            recurrence_end=original.recurrence_end,
            settings=original.settings,
            is_active=original.is_active,
        )
        self.db.add(new_template)
        self.db.flush()

        for slot in original.slots:
            new_slot = RosterTemplateSlot(
                template_id=new_template.id,
                role_id=slot.role_id,
                label=slot.label,
                sort_order=slot.sort_order,
                min_persons=slot.min_persons,
                max_persons=slot.max_persons,
            )
            self.db.add(new_slot)

        self.db.commit()
        self.db.refresh(new_template)
        logger.info(
            "roster_template_duplicated: original=%s new=%s", template_id, new_template.id
        )
        return new_template

    # -----------------------------------------------------------------
    # Instance management
    # -----------------------------------------------------------------
    def generate_instance(self, template_id: int, target_date: date) -> RosterInstance:
        template = self.get_template(template_id)
        instance = RosterInstance(
            template_id=template_id,
            date=target_date,
            status="draft",
            generated_at=datetime.now(timezone.utc),
        )
        self.db.add(instance)
        self.db.flush()

        # Create placeholder assignments for each template slot
        for slot in template.slots:
            assignment = RosterAssignment(
                instance_id=instance.id,
                slot_id=slot.id,
                person_id=None,
                status="pending",
            )
            self.db.add(assignment)

        if template.settings.get("keep_assignee"):
            self._copy_assignments_from_previous(instance)

        self.db.commit()
        self.db.refresh(instance)
        logger.info(
            "roster_instance_generated: instance_id=%s template_id=%s date=%s",
            instance.id, template_id, target_date,
        )
        return instance

    def publish_instance(self, instance_id: int) -> RosterInstance:
        instance = self.get_instance(instance_id)
        if instance.status != "draft":
            raise RosterValidationError(
                f"Cannot publish instance with status '{instance.status}'"
            )
        instance.status = "published"
        instance.published_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(instance)
        logger.info("roster_instance_published: instance_id=%s", instance_id)
        return instance

    def cancel_instance(self, instance_id: int) -> RosterInstance:
        instance = self.get_instance(instance_id)
        if instance.status in ("completed", "cancelled"):
            raise RosterValidationError(
                f"Cannot cancel instance with status '{instance.status}'"
            )
        instance.status = "cancelled"
        # Cancel all pending assignments
        for assignment in instance.assignments:
            if assignment.status == "pending":
                assignment.status = "cancelled"
                assignment.cancelled_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(instance)
        logger.info("roster_instance_cancelled: instance_id=%s", instance_id)
        return instance

    def complete_instance(self, instance_id: int) -> RosterInstance:
        instance = self.get_instance(instance_id)
        if instance.status != "published":
            raise RosterValidationError(
                f"Can only complete published instances, got '{instance.status}'"
            )
        instance.status = "completed"
        instance.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(instance)
        logger.info("roster_instance_completed: instance_id=%s", instance_id)
        return instance

    def list_instances(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        ministry_id: Optional[int] = None,
    ) -> list[RosterInstance]:
        query = (
            self.db.query(RosterInstance)
            .options(
                joinedload(RosterInstance.assignments),
                joinedload(RosterInstance.template).joinedload(RosterTemplate.slots),
            )
        )
        if date_from:
            query = query.filter(RosterInstance.date >= date_from)
        if date_to:
            query = query.filter(RosterInstance.date <= date_to)
        if ministry_id is not None:
            query = query.join(RosterTemplate).filter(
                RosterTemplate.ministry_id == ministry_id
            )
        return query.order_by(RosterInstance.date, RosterTemplate.name).all()

    def list_parish_instances(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        status: Optional[str] = None,
    ) -> list[RosterInstance]:
        """Return instances from parish-wide templates (ministry_id IS NULL)."""
        query = (
            self.db.query(RosterInstance)
            .options(
                joinedload(RosterInstance.assignments),
                joinedload(RosterInstance.template).joinedload(RosterTemplate.slots),
            )
            .join(RosterTemplate)
            .filter(RosterTemplate.ministry_id.is_(None))
        )
        if date_from:
            query = query.filter(RosterInstance.date >= date_from)
        if date_to:
            query = query.filter(RosterInstance.date <= date_to)
        if status:
            query = query.filter(RosterInstance.status == status)
        return query.order_by(RosterInstance.date, RosterTemplate.name).all()

    def get_instance(self, instance_id: int) -> RosterInstance:
        instance = (
            self.db.query(RosterInstance)
            .options(
                joinedload(RosterInstance.assignments)
                .joinedload(RosterAssignment.person),
                joinedload(RosterInstance.assignments)
                .joinedload(RosterAssignment.slot),
                joinedload(RosterInstance.template),
            )
            .filter(RosterInstance.id == instance_id)
            .first()
        )
        if instance is None:
            raise RosterValidationError(f"RosterInstance {instance_id} not found")
        return instance

    # -----------------------------------------------------------------
    # Assignment management
    # -----------------------------------------------------------------
    def assign_person(
        self, instance_id: int, slot_id: int, person_id: int, assigned_by: Optional[int] = None
    ) -> RosterAssignment:
        self._validate_person_exists(person_id)
        slot = self.db.get(RosterTemplateSlot, slot_id)
        if slot is None:
            raise RosterValidationError(f"RosterTemplateSlot {slot_id} not found")

        # Check role requirement
        if not self._validate_person_has_role(person_id, slot.role_id):
            raise RosterValidationError(
                f"Person {person_id} does not have required role",
                detail={"missing_role": slot.role_id, "person_id": person_id},
            )

        # Check capacity
        self._validate_slot_capacity(instance_id, slot_id, slot.max_persons)

        # Check for existing placeholder — reuse it instead of creating duplicate
        placeholder = (
            self.db.query(RosterAssignment)
            .filter(
                RosterAssignment.instance_id == instance_id,
                RosterAssignment.slot_id == slot_id,
                RosterAssignment.person_id.is_(None),
            )
            .first()
        )
        if placeholder:
            placeholder.person_id = person_id
            placeholder.status = "pending"
            placeholder.assigned_by = assigned_by
            placeholder.assigned_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(placeholder)
            logger.info(
                "roster_person_assigned: assignment_id=%s person_id=%s (reused placeholder)",
                placeholder.id, person_id,
            )
            return placeholder

        # Check not already assigned to same slot in instance
        existing = (
            self.db.query(RosterAssignment)
            .filter(
                RosterAssignment.instance_id == instance_id,
                RosterAssignment.slot_id == slot_id,
                RosterAssignment.person_id == person_id,
            )
            .first()
        )
        if existing:
            raise RosterValidationError(
                f"Person {person_id} is already assigned to this slot"
            )

        assignment = RosterAssignment(
            instance_id=instance_id,
            slot_id=slot_id,
            person_id=person_id,
            status="pending",
            assigned_by=assigned_by,
            assigned_at=datetime.now(timezone.utc),
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        logger.info(
            "roster_assignment_created: assignment_id=%s instance_id=%s person_id=%s",
            assignment.id, instance_id, person_id,
        )
        return assignment

    def self_assign(
        self, instance_id: int, slot_id: int, person_id: int
    ) -> RosterAssignment:
        self._validate_person_exists(person_id)
        slot = self.db.get(RosterTemplateSlot, slot_id)
        if slot is None:
            raise RosterValidationError(f"RosterTemplateSlot {slot_id} not found")

        if not self._validate_person_has_role(person_id, slot.role_id):
            raise RosterValidationError(
                f"Person {person_id} does not have required role",
                detail={"missing_role": slot.role_id, "person_id": person_id},
            )

        self._validate_slot_capacity(instance_id, slot_id, slot.max_persons)

        # Check for existing placeholder assignment — update it instead of creating duplicate
        existing = (
            self.db.query(RosterAssignment)
            .filter(
                RosterAssignment.instance_id == instance_id,
                RosterAssignment.slot_id == slot_id,
                RosterAssignment.person_id.is_(None),
            )
            .first()
        )
        if existing:
            existing.person_id = person_id
            existing.status = "accepted"
            existing.assigned_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(existing)
            logger.info(
                "roster_self_assigned: assignment_id=%s person_id=%s (reused placeholder)",
                existing.id, person_id,
            )
            return existing

        assignment = RosterAssignment(
            instance_id=instance_id,
            slot_id=slot_id,
            person_id=person_id,
            status="accepted",  # Auto-accepted
            assigned_at=datetime.now(timezone.utc),
        )
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        logger.info(
            "roster_self_assigned: assignment_id=%s person_id=%s", assignment.id, person_id
        )
        return assignment

    def update_assignment_status(
        self,
        assignment_id: int,
        status: str,
        person_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> RosterAssignment:
        assignment = (
            self.db.query(RosterAssignment)
            .options(joinedload(RosterAssignment.person))
            .filter(RosterAssignment.id == assignment_id)
            .first()
        )
        if assignment is None:
            raise RosterValidationError(f"RosterAssignment {assignment_id} not found")

        # If person_id provided, verify ownership (for member self-service)
        if person_id is not None and assignment.person_id != person_id:
            raise RosterValidationError("You can only update your own assignments")

        self._validate_status_transition(assignment.status, status)

        assignment.status = status
        timestamp_map = {
            "accepted": "accepted_at",
            "declined": "declined_at",
            "completed": "completed_at",
            "cancelled": "cancelled_at",
        }
        attr_name = timestamp_map.get(status)
        if attr_name:
            setattr(assignment, attr_name, datetime.now(timezone.utc))

        if notes is not None:
            assignment.notes = notes

        self.db.commit()
        self.db.refresh(assignment)
        logger.info(
            "roster_assignment_updated: assignment_id=%s status=%s", assignment_id, status
        )
        return assignment

    def cancel_assignment(
        self, assignment_id: int, person_id: Optional[int] = None
    ) -> RosterAssignment:
        """Cancel an assignment and free the slot for others."""
        assignment = self.update_assignment_status(assignment_id, "cancelled", person_id)
        # Free the slot — reset to placeholder so others can take it
        assignment.person_id = None
        assignment.status = "pending"
        assignment.assigned_at = None
        assignment.accepted_at = None
        assignment.cancelled_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def remove_assignment(self, assignment_id: int) -> None:
        assignment = self.db.get(RosterAssignment, assignment_id)
        if assignment is None:
            raise RosterValidationError(f"RosterAssignment {assignment_id} not found")
        self.db.delete(assignment)
        self.db.commit()
        logger.info("roster_assignment_removed: assignment_id=%s", assignment_id)

    # -----------------------------------------------------------------
    # Swap management
    # -----------------------------------------------------------------
    def propose_swap(
        self, assignment_id: int, from_person_id: int, to_person_id: int, notes: Optional[str] = None
    ) -> RosterSwapRequest:
        assignment = self.db.get(RosterAssignment, assignment_id)
        if assignment is None:
            raise RosterValidationError(f"RosterAssignment {assignment_id} not found")
        if assignment.person_id != from_person_id:
            raise RosterValidationError("You can only propose swaps for your own assignments")

        swap = RosterSwapRequest(
            assignment_id=assignment_id,
            from_person_id=from_person_id,
            to_person_id=to_person_id,
            status="pending",
            notes=notes,
        )
        self.db.add(swap)
        self.db.commit()
        self.db.refresh(swap)
        logger.info(
            "roster_swap_proposed: swap_id=%s from=%s to=%s", swap.id, from_person_id, to_person_id
        )
        return swap

    def accept_swap(self, swap_id: int, person_id: int) -> RosterSwapRequest:
        swap = (
            self.db.query(RosterSwapRequest)
            .options(joinedload(RosterSwapRequest.assignment))
            .filter(RosterSwapRequest.id == swap_id)
            .first()
        )
        if swap is None:
            raise RosterValidationError(f"RosterSwapRequest {swap_id} not found")
        if swap.status != "pending":
            raise RosterValidationError(f"Swap is already {swap.status}")
        if swap.to_person_id != person_id:
            raise RosterValidationError("Only the recipient can accept a swap")

        # Transfer the assignment
        swap.status = "accepted"
        swap.resolved_at = datetime.now(timezone.utc)

        # Create new assignment for the accepting person
        new_assignment = RosterAssignment(
            instance_id=swap.assignment.instance_id,
            slot_id=swap.assignment.slot_id,
            person_id=person_id,
            status="accepted",
            assigned_at=datetime.now(timezone.utc),
            notes=f"Swapped from person {swap.from_person_id}",
        )

        # Cancel the old assignment
        swap.assignment.status = "cancelled"
        swap.assignment.cancelled_at = datetime.now(timezone.utc)

        self.db.add(new_assignment)
        self.db.commit()
        self.db.refresh(swap)
        logger.info("roster_swap_accepted: swap_id=%s", swap_id)
        return swap

    def decline_swap(self, swap_id: int, person_id: int) -> RosterSwapRequest:
        swap = self.db.get(RosterSwapRequest, swap_id)
        if swap is None:
            raise RosterValidationError(f"RosterSwapRequest {swap_id} not found")
        if swap.status != "pending":
            raise RosterValidationError(f"Swap is already {swap.status}")
        if swap.to_person_id != person_id:
            raise RosterValidationError("Only the recipient can decline a swap")
        swap.status = "declined"
        swap.resolved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(swap)
        logger.info("roster_swap_declined: swap_id=%s", swap_id)
        return swap

    def cancel_swap(self, swap_id: int, person_id: int) -> RosterSwapRequest:
        swap = self.db.get(RosterSwapRequest, swap_id)
        if swap is None:
            raise RosterValidationError(f"RosterSwapRequest {swap_id} not found")
        if swap.status != "pending":
            raise RosterValidationError(f"Swap is already {swap.status}")
        if swap.from_person_id != person_id:
            raise RosterValidationError("Only the proposer can cancel a swap")
        swap.status = "cancelled"
        swap.resolved_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(swap)
        logger.info("roster_swap_cancelled: swap_id=%s", swap_id)
        return swap

    # -----------------------------------------------------------------
    # Query helpers
    # -----------------------------------------------------------------
    def get_my_assignments(
        self,
        person_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[RosterAssignment]:
        query = (
            self.db.query(RosterAssignment)
            .options(
                joinedload(RosterAssignment.instance).joinedload(RosterInstance.template),
                joinedload(RosterAssignment.slot),
            )
            .join(RosterInstance)  # Always join — needed for ordering and optional filters
            .filter(RosterAssignment.person_id == person_id)
        )
        if date_from:
            query = query.filter(RosterInstance.date >= date_from)
        if date_to:
            query = query.filter(RosterInstance.date <= date_to)
        return query.order_by(RosterInstance.date.asc()).all()

    def get_eligible_swappers(self, assignment_id: int) -> list[Person]:
        """People who have the matching role and aren't already assigned to this instance."""
        assignment = self.db.get(RosterAssignment, assignment_id)
        if assignment is None:
            raise RosterValidationError(f"RosterAssignment {assignment_id} not found")

        slot = assignment.slot
        instance = assignment.instance

        # People with the role who are NOT already assigned to any slot in this instance
        already_assigned = (
            self.db.query(RosterAssignment.person_id)
            .filter(RosterAssignment.instance_id == instance.id)
            .subquery()
        )

        return (
            self.db.query(Person)
            .join(PersonRosterRole, Person.id == PersonRosterRole.person_id)
            .filter(
                PersonRosterRole.role_id == slot.role_id,
                Person.id != assignment.person_id,  # Exclude the original person
                Person.id.not_in(already_assigned.select()),
            )
            .distinct()
            .all()
        )

    def get_parish_aggregate(self, target_date: date) -> list[dict]:
        """Return all rosters for a date, grouped by parish/group scope."""
        instances = (
            self.db.query(RosterInstance)
            .options(
                joinedload(RosterInstance.assignments)
                .joinedload(RosterAssignment.person),
                joinedload(RosterInstance.assignments)
                .joinedload(RosterAssignment.slot),
                joinedload(RosterInstance.template),
            )
            .filter(RosterInstance.date == target_date)
            .all()
        )
        # Group by template.ministry_id (None = parish-level)
        results = []
        for instance in instances:
            results.append({
                "id": instance.id,
                "template_id": instance.template_id,
                "template_name": instance.template.name if instance.template else None,
                "ministry_id": instance.template.ministry_id if instance.template else None,
                "date": instance.date.isoformat(),
                "status": instance.status,
                "assignment_count": len(instance.assignments),
                "fill_rate": self._calculate_fill_rate(instance),
            })
        return results

    def _calculate_fill_rate(self, instance: RosterInstance) -> float:
        """Calculate what percentage of slots are filled."""
        total_slots = len(instance.template.slots) if instance.template else 1
        if total_slots == 0:
            return 0.0
        filled = len([a for a in instance.assignments if a.status in ("accepted", "completed")])
        return round(filled / total_slots * 100, 1)

    # -----------------------------------------------------------------
    # Auto-generation
    # -----------------------------------------------------------------
    DELTA_MAP = {
        "weekly": timedelta(weeks=1),
        "biweekly": timedelta(weeks=2),
        "monthly": None,  # Special-cased below — calendar month, not 28 days
    }

    def auto_generate_instances(self, days_ahead: int = 14) -> list[RosterInstance]:
        """Generate upcoming instances for all active recurring templates.

        For each active template with recurrence_rule != 'none':
        1. Find the most recent instance date
        2. Calculate next dates based on recurrence rule
        3. Generate instances within [today, today + days_ahead]
        4. Skip dates that already have instances
        5. Apply keep_assignee for each generated instance
        6. Auto-publish instances whose publish window has arrived
        """
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        generated = []

        templates = (
            self.db.query(RosterTemplate)
            .filter(
                RosterTemplate.is_active,
                RosterTemplate.recurrence_rule != "none",
            )
            .all()
        )

        for template in templates:
            if template.recurrence_rule not in self.DELTA_MAP:
                logger.warning(
                    "Unknown recurrence_rule '%s' for template %s",
                    template.recurrence_rule, template.id,
                )
                continue

            delta = self.DELTA_MAP[template.recurrence_rule]
            recurrence_end = template.recurrence_end

            # Find most recent instance for this template
            last_instance = (
                self.db.query(RosterInstance)
                .filter(RosterInstance.template_id == template.id)
                .order_by(RosterInstance.date.desc())
                .first()
            )

            if last_instance:
                next_date = last_instance.date + delta
            else:
                # No instances yet — start from today
                next_date = today

            while next_date <= end_date:
                if recurrence_end and next_date > recurrence_end:
                    break

                # Check if instance already exists for this template+date
                existing = (
                    self.db.query(RosterInstance)
                    .filter(
                        RosterInstance.template_id == template.id,
                        RosterInstance.date == next_date,
                    )
                    .first()
                )

                if not existing:
                    instance = RosterInstance(
                        template_id=template.id,
                        date=next_date,
                        status="draft",
                        generated_at=datetime.now(timezone.utc),
                    )
                    self.db.add(instance)
                    self.db.flush()

                    if template.settings.get("keep_assignee"):
                        self._copy_assignments_from_previous(instance)

                    # Auto-publish if publish window has arrived
                    auto_open_hours = template.settings.get("auto_open_hours", 168)
                    publish_deadline = next_date - timedelta(hours=auto_open_hours)
                    if today >= publish_deadline:
                        instance.status = "published"
                        instance.published_at = datetime.now(timezone.utc)

                    generated.append(instance)
                    logger.info(
                        "auto_generated_instance: template_id=%s date=%s status=%s",
                        template.id, next_date, instance.status,
                    )

                if template.recurrence_rule == "monthly":
                    next_date = _next_month(next_date)
                else:
                    next_date += delta

        self.db.commit()
        return generated

    def auto_publish_due_instances(self) -> list[RosterInstance]:
        """Publish all draft instances whose publish window has arrived.

        An instance is due for publishing when:
        (instance.date - timedelta(hours=auto_open_hours)) <= today
        """
        today = date.today()

        # Find draft instances on active templates with auto_open_hours set
        draft_instances = (
            self.db.query(RosterInstance)
            .join(RosterTemplate)
            .filter(
                RosterInstance.status == "draft",
                RosterTemplate.is_active,
            )
            .all()
        )

        published = []
        for instance in draft_instances:
            template = instance.template
            if not template:
                continue
            auto_open_hours = template.settings.get("auto_open_hours", 168)
            publish_deadline = instance.date - timedelta(hours=auto_open_hours)
            if today >= publish_deadline:
                instance.status = "published"
                instance.published_at = datetime.now(timezone.utc)
                published.append(instance)
                logger.info(
                    "auto_published_instance: instance_id=%s date=%s",
                    instance.id, instance.date,
                )

        if published:
            self.db.commit()
        return published


def _next_month(d: date) -> date:
    """Calculate the same day next calendar month, clamping to month-end if needed."""
    year, month = d.year, d.month
    if month == 12:
        year += 1
        month = 1
    else:
        month += 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(d.day, last_day)
    return date(year, month, day)


def get_roster_service(db: Session = Depends(get_db)) -> RosterService:
    """FastAPI dependency for RosterService."""
    return RosterService(db)
