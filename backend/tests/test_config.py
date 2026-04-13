"""Tests for app.config — Settings validators and list properties."""

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from app.config import Settings


VALID_SECRET = "a]3$kG9!mZ2@vX7&qR4*wN6+tY1%cF0x"  # 34 chars


@pytest.fixture(autouse=True)
def _set_required_env(monkeypatch):
    """Ensure required env vars are always available and .env is ignored."""
    monkeypatch.setenv("SECRET_KEY", VALID_SECRET)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    # Clear any cached module state if needed


def _settings(**env):
    """Build a Settings instance that ignores .env files."""

    class TestSettings(Settings):
        model_config = SettingsConfigDict(
            env_file=None,
            extra="ignore",
        )

    return TestSettings(**env)


# ── cors_origins_list ──────────────────────────────────────────────


class TestCorsOriginsList:
    def test_default_comma_separated(self):
        s = _settings()
        origins = s.cors_origins_list
        assert "http://localhost:5173" in origins
        assert "http://127.0.0.1:5173" in origins

    def test_comma_separated_custom(self):
        s = _settings(cors_origins="https://a.com,https://b.com")
        assert s.cors_origins_list == ["https://a.com", "https://b.com"]

    def test_json_list_parsed(self):
        s = _settings(cors_origins='["https://x.com","https://y.com"]')
        assert s.cors_origins_list == ["https://x.com", "https://y.com"]

    def test_json_decode_falls_back_to_comma(self):
        """When JSON is malformed, fall back to comma-split."""
        s = _settings(cors_origins="[broken json")
        assert s.cors_origins_list == ["[broken json"]

    def test_json_non_list_falls_back_to_comma(self):
        """JSON parses but isn't a list → comma fallback."""
        s = _settings(cors_origins='"https://single.com"')
        assert s.cors_origins_list == ['"https://single.com"']

    def test_whitespace_stripped(self):
        s = _settings(cors_origins=" https://a.com , https://b.com ")
        assert s.cors_origins_list == ["https://a.com", "https://b.com"]

    def test_empty_segments_skipped(self):
        s = _settings(cors_origins="https://a.com,,https://b.com,")
        assert s.cors_origins_list == ["https://a.com", "https://b.com"]


# ── authorized_emails_list ─────────────────────────────────────────


class TestAuthorizedEmailsList:
    def test_empty_string(self):
        s = _settings(authorized_emails="")
        assert s.authorized_emails_list == []

    def test_single_email(self):
        s = _settings(authorized_emails="admin@parish.org")
        assert s.authorized_emails_list == ["admin@parish.org"]

    def test_multiple_emails(self):
        s = _settings(authorized_emails="a@b.com,c@d.com,e@f.com")
        assert s.authorized_emails_list == ["a@b.com", "c@d.com", "e@f.com"]

    def test_whitespace_stripped(self):
        s = _settings(authorized_emails=" a@b.com , c@d.com ")
        assert s.authorized_emails_list == ["a@b.com", "c@d.com"]

    def test_empty_segments_skipped(self):
        s = _settings(authorized_emails="a@b.com,,c@d.com,")
        assert s.authorized_emails_list == ["a@b.com", "c@d.com"]


# ── validate_secret_key ────────────────────────────────────────────


class TestValidateSecretKey:
    def test_rejects_default_string(self):
        with pytest.raises(ValidationError, match="secure value"):
            _settings(secret_key="change-me-in-production")

    def test_rejects_empty(self):
        with pytest.raises(ValidationError, match="secure value"):
            _settings(secret_key="")

    def test_rejects_short_key(self):
        with pytest.raises(ValidationError, match="32 characters"):
            _settings(secret_key="short-key")

    def test_accepts_32_char_key(self):
        s = _settings(secret_key=VALID_SECRET)
        assert s.secret_key == VALID_SECRET
