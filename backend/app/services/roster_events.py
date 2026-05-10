"""Roster event emitter — bridges roster actions to the notification system."""

import logging
from datetime import date

from app.services.notifications import notification_service

logger = logging.getLogger("parish.roster.events")


class RosterEventEmitter:
    """Emits roster events to centralized notification system.

    Does NOT send email/SMS directly — the notification system handles delivery.
    All methods are fire-and-forget — they don't block the triggering action.
    """

    # -----------------------------------------------------------------
    # Assignment events
    # -----------------------------------------------------------------
    @staticmethod
    def emit_assignment_created(assignment, template_name: str, slot_label: str, event_date: date) -> None:
        """Leader assigns person to slot."""
        notification_service.emit(
            event_type="roster.assignment.created",
            recipients=[assignment.person_id],
            category="roster",
            template_data={
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
            },
            channels=["email", "sms", "app"],
        )

    @staticmethod
    def emit_assignment_removed(person_id: int, template_name: str, slot_label: str, event_date: date) -> None:
        """Post-publish edit removes person from slot."""
        notification_service.emit(
            event_type="roster.assignment.removed",
            recipients=[person_id],
            category="roster",
            template_data={
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
            },
            channels=["email", "sms", "app"],
        )

    @staticmethod
    def emit_assignment_cancelled(assignment, template_name: str, slot_label: str, event_date: date) -> None:
        """Member cancels their own assignment — notify leader."""
        # In full impl, look up leader from template.ministry.leader_id
        notification_service.emit(
            event_type="roster.assignment.cancelled",
            recipients=[],  # Will be filled by notification system leader lookup
            category="roster",
            template_data={
                "person_id": assignment.person_id,
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
            },
            channels=["email", "app"],
        )

    @staticmethod
    def emit_assignment_declined(assignment, template_name: str, slot_label: str, event_date: date) -> None:
        """Member declines assignment — notify leader."""
        notification_service.emit(
            event_type="roster.assignment.declined",
            recipients=[],  # Leader lookup
            category="roster",
            template_data={
                "person_id": assignment.person_id,
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
            },
            channels=["email", "app"],
        )

    # -----------------------------------------------------------------
    # Role events
    # -----------------------------------------------------------------
    @staticmethod
    def emit_role_assigned(person_id: int, role_name: str) -> None:
        """Inline role prompt accepted."""
        notification_service.emit(
            event_type="roster.role.assigned",
            recipients=[person_id],
            category="roster",
            template_data={"role": role_name},
            channels=["app"],
        )

    # -----------------------------------------------------------------
    # Instance events
    # -----------------------------------------------------------------
    @staticmethod
    def emit_instance_published(instance, template_name: str, ministry_id: int | None, open_slot_count: int) -> None:
        """Instance published — notify members with matching roles, or leader if empty."""
        if open_slot_count == 0:
            notification_service.emit(
                event_type="roster.instance.published_empty",
                recipients=[],  # Leader lookup
                category="roster",
                template_data={
                    "date": instance.date.isoformat(),
                    "roster_name": template_name,
                    "ministry_id": ministry_id,
                },
                channels=["email", "app"],
            )
        else:
            notification_service.emit(
                event_type="roster.instance.published",
                recipients=[],  # Ministry members with matching roles
                category="roster",
                template_data={
                    "date": instance.date.isoformat(),
                    "roster_name": template_name,
                    "open_slots": open_slot_count,
                    "ministry_id": ministry_id,
                },
                channels=["email", "sms", "app"],
            )

    @staticmethod
    def emit_instance_cancelled(instance, template_name: str, assignee_ids: list[int]) -> None:
        """Instance cancelled — notify all assignees."""
        notification_service.emit(
            event_type="roster.instance.cancelled",
            recipients=assignee_ids,
            category="roster",
            template_data={
                "date": instance.date.isoformat(),
                "roster_name": template_name,
            },
            channels=["email", "sms", "app"],
        )

    # -----------------------------------------------------------------
    # Swap events
    # -----------------------------------------------------------------
    @staticmethod
    def emit_swap_requested(swap, assignment, template_name: str, slot_label: str, event_date: date) -> None:
        """Swap proposal created — notify target."""
        notification_service.emit(
            event_type="roster.swap.requested",
            recipients=[swap.to_person_id],
            category="roster",
            template_data={
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
                "swap_id": swap.id,
            },
            channels=["email", "app"],
        )

    @staticmethod
    def emit_swap_accepted(swap, assignment, template_name: str, slot_label: str, event_date: date) -> None:
        """Swap accepted — notify original assignee."""
        notification_service.emit(
            event_type="roster.swap.accepted",
            recipients=[swap.from_person_id],  # + leaders in full impl
            category="roster",
            template_data={
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
                "swap_id": swap.id,
            },
            channels=["email", "app"],
        )

    @staticmethod
    def emit_swap_declined(swap, assignment, template_name: str, slot_label: str, event_date: date) -> None:
        """Swap declined — notify proposer."""
        notification_service.emit(
            event_type="roster.swap.declined",
            recipients=[swap.from_person_id],
            category="roster",
            template_data={
                "slot": slot_label,
                "date": event_date.isoformat(),
                "roster_name": template_name,
                "swap_id": swap.id,
            },
            channels=["email", "app"],
        )
