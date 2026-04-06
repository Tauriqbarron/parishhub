"""Structured JSON logging for security events and unhandled exceptions.

12-Factor + OWASP compliance:
- All log entries are JSON for machine parsing
- Includes request-id, user-agent, and timestamp
- Unhandled exception handler captures traceback in structured format
- Security events (auth failures, rate limits, forbidden access)
  get extra context fields
"""

import json
import logging
import sys
import traceback
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON for log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request context if available (set by ContextMiddleware)
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_agent"):
            log_entry["user_agent"] = record.user_agent
        if hasattr(record, "user_email"):
            log_entry["user_email"] = record.user_email

        # Exception info
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Extra fields from log call
        if hasattr(record, "extra"):
            log_entry["extra"] = record.extra

        # Security classification
        if hasattr(record, "security_event"):
            log_entry["security_event"] = record.security_event

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class RequestContextFilter(logging.Filter):
    """Inject request context into log records."""

    def __init__(self):
        super().__init__()
        self._request_id: str | None = None
        self._user_agent: str | None = None
        self._user_email: str | None = None

    def set_context(self, request_id: str, user_agent: str, user_email: str | None):
        self._request_id = request_id
        self._user_agent = user_agent
        self._user_email = user_email

    def filter(self, record: logging.LogRecord) -> bool:
        if self._request_id:
            record.request_id = self._request_id
        if self._user_agent:
            record.user_agent = self._user_agent
        if self._user_email:
            record.user_email = self._user_email
        return True


# Global context filter — set by middleware per-request
request_context = RequestContextFilter()


def setup_logging(json_logs: bool = True) -> logging.Logger:
    """Configure structured logging for the application.

    Args:
        json_logs: If True (default), use JSON formatting.
                   If False, use human-readable format (dev mode).
    """
    root = logging.getLogger("parish")
    root.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if json_logs:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    handler.addFilter(request_context)
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ["uvicorn.access", "sqlalchemy.engine", "slowapi"]:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    return root


def log_security_event(logger: logging.Logger, event_type: str, **kwargs):
    """Log a security-relevant event with consistent structure.

    Usage:
        log_security_event(logger, "auth_failure", email=user_email, ip=client_ip)
        log_security_event(logger, "forbidden_access", resource="persons", user_id=uid)
        log_security_event(logger, "rate_limit_exceeded", endpoint="/api/persons")
    """
    record = logger.makeRecord(
        name=logger.name,
        level=logging.WARNING,
        fn="(security)",
        lno=0,
        msg=f"SECURITY: {event_type}",
        args=(),
        exc_info=None,
    )
    record.security_event = event_type
    record.extra = kwargs
    logger.handle(record)
