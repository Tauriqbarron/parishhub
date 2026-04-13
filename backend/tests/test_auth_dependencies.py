"""Tests for app/auth/dependencies.py — auth dependency coverage."""

import hashlib
import hmac
import time

import pytest

from app.auth.dependencies import User, require_auth, verify_signature
from app.config import settings


def _make_auth_headers(email: str = "test@example.com") -> dict[str, str]:
    """Build valid auth headers with a correct HMAC signature."""
    ts = str(int(time.time()))
    msg = f"{ts}.{email}"
    sig = hmac.new(
        settings.auth_secret.encode(), msg.encode(), hashlib.sha256
    ).hexdigest()
    return {
        "X-User-Email": email,
        "X-Auth-Timestamp": ts,
        "X-Auth-Signature": sig,
        "X-User-Name": "Test",
    }


# ---------------------------------------------------------------------------
# verify_signature
# ---------------------------------------------------------------------------


class TestVerifySignature:
    """Unit-level tests for the verify_signature helper."""

    def test_empty_secret_returns_false(self, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "")
        assert verify_signature("a@b.com", str(int(time.time())), "deadbeef") is False

    def test_expired_timestamp_returns_false(self, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        expired_ts = str(int(time.time()) - 301)
        email = "a@b.com"
        msg = f"{expired_ts}.{email}"
        sig = hmac.new(
            settings.auth_secret.encode(), msg.encode(), hashlib.sha256
        ).hexdigest()
        assert verify_signature(email, expired_ts, sig) is False

    def test_invalid_timestamp_returns_false(self, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        assert verify_signature("a@b.com", "not-a-number", "deadbeef") is False

    def test_wrong_signature_returns_false(self, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        ts = str(int(time.time()))
        assert verify_signature("a@b.com", ts, "completely-wrong-sig") is False

    def test_valid_signature_returns_true(self, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        ts = str(int(time.time()))
        email = "a@b.com"
        msg = f"{ts}.{email}"
        sig = hmac.new(
            settings.auth_secret.encode(), msg.encode(), hashlib.sha256
        ).hexdigest()
        assert verify_signature(email, ts, sig) is True


# ---------------------------------------------------------------------------
# get_current_user (exercised through the test client)
# ---------------------------------------------------------------------------


class TestGetCurrentUser:
    """Tests for get_current_user via the FastAPI test client."""

    def test_missing_email_header_returns_401(self, client):
        """No X-User-Email → get_current_user returns None → require_auth 401."""
        resp = client.get("/api/me", headers={})
        assert resp.status_code == 401

    def test_missing_timestamp_header_returns_401(self, client, monkeypatch):
        """Missing X-Auth-Timestamp / X-Auth-Signature → 401."""
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        headers = {"X-User-Email": "test@example.com"}
        resp = client.get("/api/me", headers=headers)
        assert resp.status_code == 401

    def test_invalid_signature_returns_401(self, client, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        monkeypatch.setattr(settings, "authorized_emails", "test@example.com")
        ts = str(int(time.time()))
        headers = {
            "X-User-Email": "test@example.com",
            "X-Auth-Timestamp": ts,
            "X-Auth-Signature": "bad-sig",
            "X-User-Name": "Test",
        }
        resp = client.get("/api/me", headers=headers)
        assert resp.status_code == 401

    def test_unauthorized_email_returns_401(self, client, monkeypatch):
        """Valid signature but email not in authorized_emails_list → 401."""
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        monkeypatch.setattr(settings, "authorized_emails", "admin@example.com")
        headers = _make_auth_headers("intruder@example.com")
        resp = client.get("/api/me", headers=headers)
        assert resp.status_code == 401

    def test_valid_headers_returns_200(self, client, monkeypatch):
        monkeypatch.setattr(settings, "auth_secret", "test-secret-1234567890")
        monkeypatch.setattr(settings, "authorized_emails", "test@example.com")
        headers = _make_auth_headers()
        resp = client.get("/api/me", headers=headers)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# require_auth (direct call)
# ---------------------------------------------------------------------------


class TestRequireAuth:
    """Direct unit tests for the require_auth dependency."""

    def test_none_user_raises_401(self):
        with pytest.raises(Exception) as exc_info:
            # require_auth is async but the raise happens synchronously
            import asyncio

            asyncio.get_event_loop().run_until_complete(require_auth(None))
        assert exc_info.value.status_code == 401  # type: ignore[attr-defined]

    def test_valid_user_returns_user(self):
        user = User(email="a@b.com", name="Alice")
        import asyncio

        result = asyncio.get_event_loop().run_until_complete(require_auth(user))
        assert result.email == "a@b.com"
        assert result.name == "Alice"
