"""Notification cron jobs — N13 (#321).

Runs the reminder engine to check for upcoming deadlines and fire notifications.

Usage:
    python scripts/notification_cron.py

Schedule (via hermes cronjob):
    - every 30 minutes (catches both 24h and 48h windows reliably)
"""

import logging
import os
import sys

# Set up path for module imports when run as a standalone script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.services.reminders import ReminderEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("notification_cron")


def main():
    """Create a DB session and run all reminder checks."""
    db = SessionLocal()
    try:
        engine = ReminderEngine(db)
        results = engine.check_all()
        logger.info("notification_cron_complete: %s", results)
        return results
    except Exception:
        logger.exception("notification_cron failed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
