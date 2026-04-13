"""Tests for app.logging_config — JSONFormatter, setup_logging, log_security_event."""

import json
import logging


from app.logging_config import JSONFormatter, setup_logging, log_security_event


# ── Helpers ────────────────────────────────────────────────────────


def _make_record(msg="test", level=logging.INFO, **extra):
    """Create a LogRecord, optionally attaching extra attributes."""
    logger = logging.getLogger("test")
    record = logger.makeRecord(logger.name, level, "(test)", 1, msg, (), None)
    for k, v in extra.items():
        setattr(record, k, v)
    return record


# ── JSONFormatter.format ───────────────────────────────────────────


class TestJSONFormatter:
    def setup_method(self):
        self.fmt = JSONFormatter()

    def test_basic_fields(self):
        rec = _make_record("hello")
        out = json.loads(self.fmt.format(rec))
        assert out["level"] == "INFO"
        assert out["message"] == "hello"
        assert out["logger"] == "test"
        assert "timestamp" in out
        assert "module" in out
        assert "function" in out
        assert "line" in out

    def test_request_id(self):
        rec = _make_record(request_id="abc-123")
        out = json.loads(self.fmt.format(rec))
        assert out["request_id"] == "abc-123"

    def test_user_agent(self):
        rec = _make_record(user_agent="Mozilla/5.0")
        out = json.loads(self.fmt.format(rec))
        assert out["user_agent"] == "Mozilla/5.0"

    def test_user_email(self):
        rec = _make_record(user_email="user@example.com")
        out = json.loads(self.fmt.format(rec))
        assert out["user_email"] == "user@example.com"

    def test_exception_info(self):
        try:
            raise ValueError("boom")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        rec = _make_record()
        rec.exc_info = exc_info
        out = json.loads(self.fmt.format(rec))
        assert "exception" in out
        assert out["exception"]["type"] == "ValueError"
        assert out["exception"]["message"] == "boom"
        assert isinstance(out["exception"]["traceback"], list)
        assert any("ValueError" in line for line in out["exception"]["traceback"])

    def test_extra_field(self):
        rec = _make_record(extra={"key": "val"})
        out = json.loads(self.fmt.format(rec))
        assert out["extra"] == {"key": "val"}

    def test_security_event(self):
        rec = _make_record(security_event="auth_failure")
        out = json.loads(self.fmt.format(rec))
        assert out["security_event"] == "auth_failure"

    def test_all_attributes_together(self):
        try:
            raise RuntimeError("fail")
        except RuntimeError:
            import sys

            exc_info = sys.exc_info()
        rec = _make_record(
            request_id="rid",
            user_agent="bot",
            user_email="x@y.com",
            extra={"a": 1},
            security_event="rate_limit",
        )
        rec.exc_info = exc_info
        out = json.loads(self.fmt.format(rec))
        assert out["request_id"] == "rid"
        assert out["user_agent"] == "bot"
        assert out["user_email"] == "x@y.com"
        assert out["extra"] == {"a": 1}
        assert out["security_event"] == "rate_limit"
        assert out["exception"]["type"] == "RuntimeError"


# ── setup_logging (dev mode / human-readable) ──────────────────────


class TestSetupLogging:
    def test_returns_logger_named_parish(self):
        logger = setup_logging(json_logs=True)
        assert logger.name == "parish"
        assert logger.level == logging.INFO

    def test_dev_mode_uses_plain_formatter(self):
        logger = setup_logging(json_logs=False)
        handler = logger.handlers[0]
        assert not isinstance(handler.formatter, JSONFormatter)

    def test_json_mode_uses_json_formatter(self):
        logger = setup_logging(json_logs=True)
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)

    def test_no_duplicate_handlers(self):
        setup_logging()
        setup_logging()
        logger = logging.getLogger("parish")
        assert len(logger.handlers) == 1


# ── log_security_event ─────────────────────────────────────────────


class TestLogSecurityEvent:
    def test_emits_warning_with_security_event(self):
        logger = logging.getLogger("test_security")
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        captured = []

        class _Capture(logging.Handler):
            def emit(self, record):
                captured.append(record)

        logger.addHandler(_Capture())

        log_security_event(logger, "auth_failure", email="a@b.com", ip="1.2.3.4")

        assert len(captured) == 1
        rec = captured[0]
        assert rec.security_event == "auth_failure"
        assert rec.extra == {"email": "a@b.com", "ip": "1.2.3.4"}
        assert "SECURITY: auth_failure" in rec.getMessage()

    def test_event_appears_in_json_output(self):
        formatter = JSONFormatter()
        logger = logging.getLogger("test_json_sec")
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        captured = []

        class _Capture(logging.Handler):
            def emit(self, record):
                captured.append(record)

        logger.addHandler(_Capture())

        log_security_event(logger, "forbidden_access", resource="persons")

        rec = captured[0]
        out = json.loads(formatter.format(rec))
        assert out["security_event"] == "forbidden_access"
        assert out["extra"] == {"resource": "persons"}
        assert out["level"] == "WARNING"
