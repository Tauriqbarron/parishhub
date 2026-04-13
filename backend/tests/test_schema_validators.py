"""Tests for schema validators."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from app.schemas.mass_times import MassTimeCreate, MassTimeUpdate, parse_time
from app.schemas.person import PersonCreate


# ---------------------------------------------------------------------------
# parse_time
# ---------------------------------------------------------------------------


def test_parse_time_none():
    assert parse_time(None) is None


def test_parse_time_passthrough():
    t = time(10, 30)
    assert parse_time(t) is t


def test_parse_time_two_parts():
    assert parse_time("10:30") == time(10, 30)


def test_parse_time_three_parts():
    assert parse_time("10:30:00") == time(10, 30, 0)


def test_parse_time_invalid():
    with pytest.raises(ValueError, match="Invalid time format"):
        parse_time("invalid")


def test_parse_time_single_part_invalid():
    with pytest.raises(ValueError, match="Invalid time format"):
        parse_time("10")


# ---------------------------------------------------------------------------
# MassTimeBase / MassTimeCreate validators
# ---------------------------------------------------------------------------


def test_mass_time_create_valid():
    m = MassTimeCreate(name="Sunday Mass", time="10:30")
    assert m.time == time(10, 30)


def test_mass_time_create_none_time():
    """time=None on MassTimeCreate should be caught by the validator."""
    with pytest.raises(ValidationError):
        MassTimeCreate(name="Mass", time=None)


def test_mass_time_create_string_time():
    m = MassTimeCreate(name="Mass", time="09:00:00")
    assert m.time == time(9, 0, 0)


# ---------------------------------------------------------------------------
# MassTimeUpdate validators
# ---------------------------------------------------------------------------


def test_mass_time_update_none_time():
    """MassTimeUpdate allows time=None (partial update)."""
    result = MassTimeUpdate(time=None)
    assert result.time is None


def test_mass_time_update_valid_time():
    result = MassTimeUpdate(time="14:30")
    assert result.time == time(14, 30)


def test_mass_time_update_no_time():
    """Omitting time leaves default None."""
    result = MassTimeUpdate(name="Updated")
    assert result.time is None


# ---------------------------------------------------------------------------
# PersonCreate validators
# ---------------------------------------------------------------------------


def test_valid_phone():
    p = PersonCreate(first_name="J", last_name="S", phone="+1-555-0100")
    assert p.phone == "+1-555-0100"


def test_none_phone():
    p = PersonCreate(first_name="J", last_name="S", phone=None)
    assert p.phone is None


def test_invalid_phone():
    with pytest.raises(ValidationError):
        PersonCreate(first_name="J", last_name="S", phone="bad")


def test_future_dob():
    with pytest.raises(ValidationError, match="future"):
        PersonCreate(first_name="J", last_name="S", date_of_birth=date(2099, 1, 1))


def test_valid_dob():
    p = PersonCreate(first_name="J", last_name="S", date_of_birth=date(2000, 6, 15))
    assert p.date_of_birth == date(2000, 6, 15)


def test_none_dob():
    p = PersonCreate(first_name="J", last_name="S", date_of_birth=None)
    assert p.date_of_birth is None
