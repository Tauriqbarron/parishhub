"""Application lifespan: startup tasks and graceful shutdown.

12-Factor compliance:
- Dispose of database connection pools during shutdown so
  container termination does not leak connections.
- Log startup/shutdown events with wall-clock timing
  so operators can see how long shutdown draining took.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging
import time

from app.database import engine

logger = logging.getLogger("parish.lifespan")


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager.

    Handles:
    - Startup: initialisation tasks
    - Shutdown: graceful connection pool drain
    """

    # --- Startup ---
    startup_start = time.monotonic()
    logger.info("Application starting up...")

    if hasattr(engine, "connect"):
        # Verify DB connectivity at startup
        with engine.connect() as conn:
            _ = conn.exec_driver_sql("SELECT 1")

    startup_elapsed = time.monotonic() - startup_start
    logger.info(
        "Application ready in %.3fs | DB: %s",
        startup_elapsed,
        engine.url.render_as_string(hide_password=True),
    )

    yield

    # --- Shutdown ---
    shutdown_start = time.monotonic()
    logger.info("Shutting down — draining connections...")

    if hasattr(engine, "dispose"):
        engine.dispose()
        logger.info("Database connection pool disposed.")

    shutdown_elapsed = time.monotonic() - shutdown_start
    logger.info("Graceful shutdown completed in %.3fs", shutdown_elapsed)


__all__ = ["lifespan"]
