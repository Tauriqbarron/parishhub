"""Roster cron jobs. Run via Hermes cron or system crontab.

Usage:
    python scripts/roster_cron.py generate    # Auto-generate instances for next 14 days
    python scripts/roster_cron.py publish     # Auto-publish due draft instances
    python scripts/roster_cron.py all          # Run both

Schedule (via hermes cronjob):
    - generate: daily at 01:00 NZST
    - publish:  every hour
"""

import sys
import logging

from app.database import SessionLocal
from app.services.roster import RosterService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("roster_cron")


def generate_instances():
    """Auto-generate roster instances for all active recurring templates."""
    db = SessionLocal()
    try:
        service = RosterService(db)
        instances = service.auto_generate_instances(days_ahead=14)
        logger.info("Generated %d instances", len(instances))
        for inst in instances:
            logger.info(
                "  instance_id=%d template_id=%d date=%s status=%s",
                inst.id, inst.template_id, inst.date, inst.status,
            )
    except Exception:
        logger.exception("generate_instances failed")
        raise
    finally:
        db.close()


def publish_instances():
    """Auto-publish draft instances whose open window has arrived."""
    db = SessionLocal()
    try:
        service = RosterService(db)
        published = service.auto_publish_due_instances()
        logger.info("Published %d instances", len(published))
        for inst in published:
            logger.info(
                "  instance_id=%d template_id=%d date=%s",
                inst.id, inst.template_id, inst.date,
            )
    except Exception:
        logger.exception("publish_instances failed")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "generate"

    # Set up path for module imports
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    runners = {
        "generate": generate_instances,
        "publish": publish_instances,
        "all": lambda: (generate_instances(), publish_instances()),
    }

    runner = runners.get(cmd)
    if runner is None:
        logger.error("Unknown command: %s. Use: generate, publish, all", cmd)
        sys.exit(1)

    runner()
