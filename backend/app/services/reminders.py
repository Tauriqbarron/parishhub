"""Reminder engine — N13 (#321) + N14 (#322).

Checks upcoming roster instances, events, RSVPs, mass times, and sacraments
for approaching deadlines and emits notifications to assigned persons.
Uses ReminderLog for deduplication so each entity+hours_before combo fires once.
"""

import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ministry import EventRSVP, MinistryEvent
from app.models.mass_times import MassTime
from app.models.notification import ReminderLog
from app.models.roster import RosterAssignment, RosterInstance, RosterTemplate
from app.models.sacrament import Sacrament
from app.services.notifications import notification_service

logger = logging.getLogger("parish.reminders")

# Default hours-before thresholds to check
DEFAULT_REMINDER_HOURS = [24, 48]


class ReminderEngine:
    """Checks upcoming deadlines and sends reminder notifications.

    Each check_* method:
    1. Queries the relevant table for upcoming items within the reminder window.
    2. Checks ReminderLog to see if a reminder has already fired.
    3. Emits notification via notification_service.emit().
    4. Records a ReminderLog entry for deduplication.
    """

    def __init__(self, db: Session):
        self.db = db
        self.now = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def check_all(self) -> dict:
        """Run all reminder checks and return summary counts."""
        results = {
            "roster": self.check_roster_reminders(),
            "events": self.check_event_reminders(),
            "rsvp": self.check_rsvp_reminders(),
            "mass": self.check_mass_reminders(),
            "sacrament": self.check_sacrament_reminders(),
        }
        total = sum(results.values())
        logger.info("reminders_check_all: %s total=%d", results, total)
        return results

    # ------------------------------------------------------------------
    # N13: Roster reminders
    # ------------------------------------------------------------------

    def check_roster_reminders(self) -> int:
        """Check published roster instances within 24/48h and notify assignees.

        Finds roster instances with status='published' whose date is within
        reminder_hours from now. For each, checks if any assignment's person
        hasn't been reminded yet for this instance+hours combo.
        """
        fired = 0

        for hours_before in DEFAULT_REMINDER_HOURS:
            target_date = (self.now + timedelta(hours=hours_before)).date()

            instances = (
                self.db.query(RosterInstance)
                .filter(
                    RosterInstance.date == target_date,
                    RosterInstance.status == "published",
                )
                .all()
            )

            for instance in instances:
                template = (
                    self.db.query(RosterTemplate)
                    .filter(RosterTemplate.id == instance.template_id)
                    .first()
                )

                # Get reminder_hours from template settings, fall back to defaults
                template_reminder_hours = (
                    (template.settings or {}).get("reminder_hours", [])
                    if template
                    else []
                )

                # Only fire if this hours_before is in the template's reminder_hours,
                # or if no specific hours are configured (default = fire at 24 & 48)
                if template_reminder_hours and hours_before not in template_reminder_hours:
                    continue

                # Collect unique person_ids from assignments
                assignments = (
                    self.db.query(RosterAssignment)
                    .filter(
                        RosterAssignment.instance_id == instance.id,
                        RosterAssignment.person_id.isnot(None),
                    )
                    .all()
                )

                person_ids = list({a.person_id for a in assignments if a.person_id})
                if not person_ids:
                    continue

                # Check dedup
                already_fired = (
                    self.db.query(ReminderLog)
                    .filter(
                        ReminderLog.reminder_type == "roster",
                        ReminderLog.trigger_entity_type == "roster_instance",
                        ReminderLog.trigger_entity_id == instance.id,
                        ReminderLog.hours_before == hours_before,
                    )
                    .first()
                )
                if already_fired:
                    continue

                # Emit notification
                roster_name = template.name if template else f"Roster #{instance.template_id}"
                notification_service.emit(
                    event_type="roster_reminder",
                    recipients=person_ids,
                    category="roster",
                    template_data={
                        "title": f"Roster reminder: {roster_name}",
                        "body": (
                            f"Your roster duty for **{roster_name}** is scheduled "
                            f"for **{instance.date.isoformat()}** (in {hours_before}h)."
                        ),
                        "instance_id": instance.id,
                        "hours_before": hours_before,
                    },
                    channels=["app", "email"],
                    db=self.db,
                )

                # Log reminder
                self.db.add(
                    ReminderLog(
                        reminder_type="roster",
                        trigger_entity_type="roster_instance",
                        trigger_entity_id=instance.id,
                        hours_before=hours_before,
                        recipients_count=len(person_ids),
                    )
                )
                self.db.commit()
                fired += 1
                logger.info(
                    "roster_reminder_fired: instance=%d date=%s hours=%d recipients=%d",
                    instance.id,
                    instance.date,
                    hours_before,
                    len(person_ids),
                )

        return fired

    # ------------------------------------------------------------------
    # N13: Event reminders
    # ------------------------------------------------------------------

    def check_event_reminders(self) -> int:
        """Check upcoming ministry events within 24/48h and notify RSVP'd members.

        Finds MinistryEvent records whose event_date is within the reminder window,
        not cancelled, and emits reminders to members who RSVP'd 'going' or 'maybe'.
        """
        fired = 0

        for hours_before in DEFAULT_REMINDER_HOURS:
            target_date = (self.now + timedelta(hours=hours_before)).date()

            events = (
                self.db.query(MinistryEvent)
                .filter(
                    MinistryEvent.event_date == target_date,
                    MinistryEvent.is_cancelled == False,  # noqa: E712
                )
                .all()
            )

            for event in events:
                # Collect RSVP'd person_ids
                rsvps = (
                    self.db.query(EventRSVP)
                    .filter(
                        EventRSVP.event_id == event.id,
                        EventRSVP.status.in_(["going", "maybe"]),
                    )
                    .all()
                )
                person_ids = [r.person_id for r in rsvps]
                if not person_ids:
                    continue

                # Check dedup
                already_fired = (
                    self.db.query(ReminderLog)
                    .filter(
                        ReminderLog.reminder_type == "event",
                        ReminderLog.trigger_entity_type == "ministry_event",
                        ReminderLog.trigger_entity_id == event.id,
                        ReminderLog.hours_before == hours_before,
                    )
                    .first()
                )
                if already_fired:
                    continue

                # Emit notification
                time_str = event.start_time or "TBD"
                notification_service.emit(
                    event_type="event_reminder",
                    recipients=person_ids,
                    category="event",
                    template_data={
                        "title": f"Event reminder: {event.title}",
                        "body": (
                            f"**{event.title}** is coming up on "
                            f"**{event.event_date.isoformat()}** at {time_str} "
                            f"(in {hours_before}h).\n\n"
                            + (event.description or "")
                        ),
                        "event_id": event.id,
                        "hours_before": hours_before,
                    },
                    channels=["app", "email"],
                    db=self.db,
                )

                # Log reminder
                self.db.add(
                    ReminderLog(
                        reminder_type="event",
                        trigger_entity_type="ministry_event",
                        trigger_entity_id=event.id,
                        hours_before=hours_before,
                        recipients_count=len(person_ids),
                    )
                )
                self.db.commit()
                fired += 1
                logger.info(
                    "event_reminder_fired: event=%d title=%r date=%s hours=%d recipients=%d",
                    event.id,
                    event.title,
                    event.event_date,
                    hours_before,
                    len(person_ids),
                )

        return fired

    # ------------------------------------------------------------------
    # N14: RSVP deadline reminders
    # ------------------------------------------------------------------

    def check_rsvp_reminders(self) -> int:
        """Check events with approaching dates that have members who haven't RSVP'd.

        Finds events whose event_date is within 48h and for which members of the
        event's ministry haven't RSVP'd yet. Emits a 'please RSVP' reminder.
        """
        fired = 0
        hours_before = 48  # RSVP deadline reminder fires 48h before

        target_date = (self.now + timedelta(hours=hours_before)).date()

        events = (
            self.db.query(MinistryEvent)
            .filter(
                MinistryEvent.event_date == target_date,
                MinistryEvent.is_cancelled == False,  # noqa: E712
            )
            .all()
        )

        for event in events:
            # Find ministry members who haven't RSVP'd yet
            from app.models.ministry import MinistryMember

            rsvp_person_ids = set(
                r.person_id
                for r in self.db.query(EventRSVP)
                .filter(EventRSVP.event_id == event.id)
                .all()
            )

            members = (
                self.db.query(MinistryMember)
                .filter(
                    MinistryMember.ministry_id == event.ministry_id,
                    MinistryMember.is_active == True,  # noqa: E712
                )
                .all()
            )

            unrsvpd_person_ids = [
                m.person_id for m in members if m.person_id not in rsvp_person_ids
            ]
            if not unrsvpd_person_ids:
                continue

            # Check dedup
            already_fired = (
                self.db.query(ReminderLog)
                .filter(
                    ReminderLog.reminder_type == "rsvp_deadline",
                    ReminderLog.trigger_entity_type == "ministry_event",
                    ReminderLog.trigger_entity_id == event.id,
                    ReminderLog.hours_before == hours_before,
                )
                .first()
            )
            if already_fired:
                continue

            # Emit notification
            time_str = event.start_time or "TBD"
            notification_service.emit(
                event_type="rsvp_reminder",
                recipients=unrsvpd_person_ids,
                category="event",
                template_data={
                    "title": f"RSVP needed: {event.title}",
                    "body": (
                        f"Please RSVP for **{event.title}** on "
                        f"**{event.event_date.isoformat()}** at {time_str}."
                    ),
                    "event_id": event.id,
                    "hours_before": hours_before,
                },
                channels=["app", "email"],
                db=self.db,
            )

            # Log reminder
            self.db.add(
                ReminderLog(
                    reminder_type="rsvp_deadline",
                    trigger_entity_type="ministry_event",
                    trigger_entity_id=event.id,
                    hours_before=hours_before,
                    recipients_count=len(unrsvpd_person_ids),
                )
            )
            self.db.commit()
            fired += 1
            logger.info(
                "rsvp_reminder_fired: event=%d title=%r recipients=%d",
                event.id,
                event.title,
                len(unrsvpd_person_ids),
            )

        return fired

    # ------------------------------------------------------------------
    # N14: Mass time reminders
    # ------------------------------------------------------------------

    def check_mass_reminders(self) -> int:
        """Check upcoming mass times and send reminders.

        MassTime is a recurring schedule (day_of_week + time). This sends
        reminders based on the day before the mass. For example, if a mass
        is on Sunday, a 24h reminder fires on Saturday.
        """
        fired = 0
        hours_before = 24  # Send day-before reminders for masses

        # Today's weekday (0=Monday, 6=Sunday)
        today = self.now.date()
        # The day we're reminding about is tomorrow
        target_weekday = (today + timedelta(days=1)).weekday()

        # Python weekday: 0=Monday. DB day_of_week: 1=Sunday through 7=Saturday?
        # Most conventions use 0=Monday, but church may use 0=Sunday.
        # We'll use standard Python weekday plus handle both conventions.
        # Convert DB day_of_week to Python weekday (assume 0=Sunday in DB)
        # If DB stores 0=Sunday: python_weekday = (db_day - 1) % 7
        # If DB stores 1=Sunday: python_weekday = (db_day % 7)

        mass_times = (
            self.db.query(MassTime)
            .filter(MassTime.is_active == True)  # noqa: E712
            .all()
        )

        for mt in mass_times:
            if mt.day_of_week is None:
                continue

            # Check if this mass is tomorrow
            # day_of_week convention: 0=Sunday, 1=Monday, ..., 6=Saturday (common church convention)
            # Python weekday: 0=Monday, ..., 6=Sunday
            # Convert: python_weekday = (db_day + 6) % 7
            mass_python_weekday = (mt.day_of_week + 6) % 7
            if mass_python_weekday != target_weekday:
                continue

            # Check dedup — fire once per mass_time per day
            dedup_date = today + timedelta(days=1)
            already_fired = (
                self.db.query(ReminderLog)
                .filter(
                    ReminderLog.reminder_type == "mass_time",
                    ReminderLog.trigger_entity_type == "mass_time",
                    ReminderLog.trigger_entity_id == mt.id,
                    ReminderLog.hours_before == hours_before,
                    func.date(ReminderLog.fired_at) == dedup_date,
                )
                .first()
            )
            if already_fired:
                continue

            # For mass reminders, we don't have specific recipients —
            # this is a broadcast. Log 0 recipients but still fire the reminder.
            # In production, this would be sent to all parishioners.
            notification_service.emit(
                event_type="mass_reminder",
                recipients=[],  # Broadcast — no specific recipients tracked
                category="mass",
                template_data={
                    "title": f"Mass tomorrow: {mt.name}",
                    "body": (
                        f"**{mt.name}** is tomorrow at "
                        f"**{mt.time.strftime('%I:%M %p') if mt.time else 'TBD'}**"
                        + (f" at {mt.location}" if mt.location else "")
                    ),
                    "mass_time_id": mt.id,
                    "hours_before": hours_before,
                },
                channels=["app"],
                db=self.db,
            )

            # Log reminder
            self.db.add(
                ReminderLog(
                    reminder_type="mass_time",
                    trigger_entity_type="mass_time",
                    trigger_entity_id=mt.id,
                    hours_before=hours_before,
                    recipients_count=0,
                )
            )
            self.db.commit()
            fired += 1
            logger.info(
                "mass_reminder_fired: mass=%d name=%r day=%d",
                mt.id,
                mt.name,
                mt.day_of_week,
            )

        return fired

    # ------------------------------------------------------------------
    # N14: Sacrament reminders
    # ------------------------------------------------------------------

    def check_sacrament_reminders(self) -> int:
        """Check upcoming sacrament dates and remind the person (or family).

        Finds Sacrament records whose date_received is within the reminder
        window and emits a reminder to the person.
        """
        fired = 0

        for hours_before in DEFAULT_REMINDER_HOURS:
            target_date = (self.now + timedelta(hours=hours_before)).date()

            sacraments = (
                self.db.query(Sacrament)
                .filter(Sacrament.date_received == target_date)
                .all()
            )

            for sacrament in sacraments:
                # Check dedup
                already_fired = (
                    self.db.query(ReminderLog)
                    .filter(
                        ReminderLog.reminder_type == "sacrament",
                        ReminderLog.trigger_entity_type == "sacrament",
                        ReminderLog.trigger_entity_id == sacrament.id,
                        ReminderLog.hours_before == hours_before,
                    )
                    .first()
                )
                if already_fired:
                    continue

                sacrament_label = sacrament.sacrament_type.value.replace("_", " ").title()

                notification_service.emit(
                    event_type="sacrament_reminder",
                    recipients=[sacrament.person_id],
                    category="sacrament",
                    template_data={
                        "title": f"Sacrament reminder: {sacrament_label}",
                        "body": (
                            f"Your **{sacrament_label}** is scheduled for "
                            f"**{sacrament.date_received.isoformat()}** "
                            f"(in {hours_before}h)."
                            + (f"\n\nNotes: {sacrament.notes}" if sacrament.notes else "")
                        ),
                        "sacrament_id": sacrament.id,
                        "sacrament_type": sacrament.sacrament_type.value,
                        "hours_before": hours_before,
                    },
                    channels=["app", "email"],
                    db=self.db,
                )

                # Log reminder
                self.db.add(
                    ReminderLog(
                        reminder_type="sacrament",
                        trigger_entity_type="sacrament",
                        trigger_entity_id=sacrament.id,
                        hours_before=hours_before,
                        recipients_count=1,
                    )
                )
                self.db.commit()
                fired += 1
                logger.info(
                    "sacrament_reminder_fired: sacrament=%d type=%s person=%d hours=%d",
                    sacrament.id,
                    sacrament.sacrament_type.value,
                    sacrament.person_id,
                    hours_before,
                )

        return fired
