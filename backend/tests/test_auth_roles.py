"""Tests for RBAC auth layer."""

import pytest
from fastapi import HTTPException

from app.auth.dependencies import User
from app.auth.roles import get_user_roles, require_ministry_role, require_role
from app.models.ministry import Ministry, UserRole


@pytest.fixture
def priest_user():
    return User(email="priest@parish.com", name="Father Test")


@pytest.fixture
def member_user():
    return User(email="member@parish.com", name="Member Test")


@pytest.fixture
def setup_roles(db_session):
    """Set up test roles."""
    ministry = Ministry(name="Test Ministry")
    db_session.add(ministry)
    db_session.flush()

    roles = [
        UserRole(user_email="priest@parish.com", role="priest", ministry_id=None),
        UserRole(user_email="member@parish.com", role="member", ministry_id=ministry.id),
    ]
    for r in roles:
        db_session.add(r)
    db_session.commit()
    return ministry


class TestRequireRole:
    def test_priest_passes_priest_check(self, priest_user, db_session, setup_roles):
        check = require_role("priest")
        result = check(priest_user, db_session)
        assert result.email == "priest@parish.com"

    def test_member_fails_priest_check(self, member_user, db_session, setup_roles):
        check = require_role("priest")
        with pytest.raises(HTTPException) as exc_info:
            check(member_user, db_session)
        assert exc_info.value.status_code == 403

    def test_priest_passes_admin_check(self, priest_user, db_session, setup_roles):
        check = require_role("priest", "admin")
        result = check(priest_user, db_session)
        assert result is not None


class TestRequireMinistryRole:
    def test_priest_bypasses_ministry_scope(self, priest_user, db_session, setup_roles):
        check = require_ministry_role(setup_roles.id, "leader", "member")
        result = check(priest_user, db_session)
        assert result is not None

    def test_member_passes_own_ministry(self, member_user, db_session, setup_roles):
        check = require_ministry_role(setup_roles.id, "member")
        result = check(member_user, db_session)
        assert result is not None

    def test_member_fails_other_ministry(self, member_user, db_session, setup_roles):
        check = require_ministry_role(9999, "member")
        with pytest.raises(HTTPException) as exc_info:
            check(member_user, db_session)
        assert exc_info.value.status_code == 403


class TestGetUserRoles:
    def test_get_roles_returns_correct(self, priest_user, db_session, setup_roles):
        roles = get_user_roles(priest_user, db_session)
        assert len(roles) == 1
        assert roles[0].role == "priest"

    def test_get_roles_empty_for_unknown(self, db_session, setup_roles):
        user = User(email="nobody@parish.com", name="Nobody")
        roles = get_user_roles(user, db_session)
        assert len(roles) == 0
