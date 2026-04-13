"""Edge-case tests for RegistrationService to push coverage from ~90% to 97%+.

Targets uncovered lines in app/services/registration.py:
- Line 55: _get_request_ip with None request
- Line 83: invalid temp_id in relationships
- Line 90: invalid relationship type
- Line 100: duplicate relationship skip
- Line 130: individual_person_id path in _validate_and_build_sacraments
- Line 134: empty sacrament type / whitespace-only
- Line 153: missing sacrament date
- Line 159: future sacrament date
- Line 174: whitespace-only church name
- Line 182: whitespace-only minister name
- Lines 221/231: consent storage
- Lines 291/298: _auto_create_births skips
- Line 371: get_registration_service dependency
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.registration import RegistrationService, get_registration_service


# ---------------------------------------------------------------------------
# _get_request_ip(None)
# ---------------------------------------------------------------------------


class TestGetRequestIp:
    """Tests for _get_request_ip helper."""

    def test_request_none_returns_none(self, db_session):
        svc = RegistrationService(db_session)
        assert svc._get_request_ip(None) is None

    def test_request_with_no_client_returns_none(self, db_session):
        svc = RegistrationService(db_session)
        request = MagicMock()
        request.client = None
        assert svc._get_request_ip(request) is None

    def test_request_with_client_returns_host(self, db_session):
        svc = RegistrationService(db_session)
        request = MagicMock()
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        assert svc._get_request_ip(request) == "127.0.0.1"


# ---------------------------------------------------------------------------
# _validate_and_build_sacraments edge cases
# ---------------------------------------------------------------------------


class TestSacramentValidationEdgeCases:
    """Edge cases for sacrament validation."""

    def _make_sac(self, **overrides):
        """Create a mock sacrament object."""
        sac = MagicMock()
        sac.member_temp_id = overrides.get("member_temp_id", "t1")
        sac.sacrament_type = overrides.get("sacrament_type", "baptism")
        sac.date = overrides.get("date", date(2020, 1, 1))
        sac.church = overrides.get("church", "St. Mary")
        sac.minister = overrides.get("minister", "Fr. John")
        sac.godfather = None
        sac.godmother = None
        sac.sponsor = None
        sac.parish = None
        sac.witness1 = None
        sac.witness2 = None
        sac.officiant = None
        sac.notes = None
        return sac

    def test_empty_sacrament_type_raises(self, db_session):
        svc = RegistrationService(db_session)
        sac = self._make_sac(sacrament_type="")
        with pytest.raises(HTTPException) as exc_info:
            svc._validate_and_build_sacraments([sac], {"t1": 1})
        assert "Sacrament type cannot be empty" in exc_info.value.detail

    def test_whitespace_only_sacrament_type_raises(self, db_session):
        svc = RegistrationService(db_session)
        sac = self._make_sac(sacrament_type="   ")
        with pytest.raises(HTTPException) as exc_info:
            svc._validate_and_build_sacraments([sac], {"t1": 1})
        assert "Sacrament type cannot be empty" in exc_info.value.detail

    def test_missing_sacrament_date_raises(self, db_session):
        svc = RegistrationService(db_session)
        sac = self._make_sac(date=None)
        with pytest.raises(HTTPException) as exc_info:
            svc._validate_and_build_sacraments([sac], {"t1": 1})
        assert "Sacrament date is required" in exc_info.value.detail

    def test_future_sacrament_date_raises(self, db_session):
        svc = RegistrationService(db_session)
        future = date.today() + timedelta(days=30)
        sac = self._make_sac(date=future)
        with pytest.raises(HTTPException) as exc_info:
            svc._validate_and_build_sacraments([sac], {"t1": 1})
        assert "cannot be in the future" in exc_info.value.detail

    def test_invalid_temp_id_raises(self, db_session):
        svc = RegistrationService(db_session)
        sac = self._make_sac(member_temp_id="nonexistent")
        with pytest.raises(HTTPException) as exc_info:
            svc._validate_and_build_sacraments([sac], {"t1": 1})
        assert "Invalid sacrament: member temp_id" in exc_info.value.detail

    def test_individual_person_id_skips_temp_id_lookup(self, db_session):
        """When individual_person_id is set, temp_id lookup is bypassed."""
        svc = RegistrationService(db_session)
        sac = self._make_sac(member_temp_id="ignored")
        result = svc._validate_and_build_sacraments([sac], {}, individual_person_id=42)
        assert len(result) == 1
        assert result[0][1] == 42  # person_id


# ---------------------------------------------------------------------------
# _create_sacrament_records edge cases
# ---------------------------------------------------------------------------


class TestCreateSacramentRecordsEdgeCases:
    """Edge cases for _create_sacrament_records."""

    def test_whitespace_only_church_raises(self, db_session):
        svc = RegistrationService(db_session)
        sac = MagicMock()
        sac.member_temp_id = "t1"
        sac.sacrament_type = "baptism"
        sac.date = date(2020, 1, 1)
        sac.church = "   "  # whitespace only — triggers error
        sac.minister = None
        sac.godfather = None
        sac.godmother = None
        sac.sponsor = None
        sac.parish = None
        sac.witness1 = None
        sac.witness2 = None
        sac.officiant = None
        sac.notes = None

        from app.models.sacrament import SacramentType

        validated = [(sac, 1, SacramentType.BAPTISM)]
        with pytest.raises(HTTPException) as exc_info:
            svc._create_sacrament_records(validated)
        assert "Church name cannot be empty" in exc_info.value.detail

    def test_whitespace_only_minister_raises(self, db_session):
        svc = RegistrationService(db_session)
        sac = MagicMock()
        sac.member_temp_id = "t1"
        sac.sacrament_type = "baptism"
        sac.date = date(2020, 1, 1)
        sac.church = "St. Mary"
        sac.minister = "   "  # whitespace only — triggers error
        sac.godfather = None
        sac.godmother = None
        sac.sponsor = None
        sac.parish = None
        sac.witness1 = None
        sac.witness2 = None
        sac.officiant = None
        sac.notes = None

        from app.models.sacrament import SacramentType

        validated = [(sac, 1, SacramentType.BAPTISM)]
        with pytest.raises(HTTPException) as exc_info:
            svc._create_sacrament_records(validated)
        assert "Minister name cannot be empty" in exc_info.value.detail

    def test_none_church_and_minister_ok(self, db_session):
        """None church/minister should NOT raise — only whitespace-only strings do."""
        svc = RegistrationService(db_session)
        from app.models.person import Person

        person = Person(first_name="Test", last_name="User")
        db_session.add(person)
        db_session.flush()

        sac = MagicMock()
        sac.member_temp_id = "t1"
        sac.sacrament_type = "baptism"
        sac.date = date(2020, 1, 1)
        sac.church = None
        sac.minister = None
        sac.godfather = None
        sac.godmother = None
        sac.sponsor = None
        sac.parish = None
        sac.witness1 = None
        sac.witness2 = None
        sac.officiant = None
        sac.notes = None

        from app.models.sacrament import SacramentType

        validated = [(sac, person.id, SacramentType.BAPTISM)]
        # Should not raise
        svc._create_sacrament_records(validated)


# ---------------------------------------------------------------------------
# _create_relationships edge cases
# ---------------------------------------------------------------------------


class TestCreateRelationshipsEdgeCases:
    """Edge cases for _create_relationships."""

    def test_invalid_from_temp_id_raises(self, db_session):
        svc = RegistrationService(db_session)
        rel = MagicMock()
        rel.from_temp_id = "bad"
        rel.to_temp_id = "t2"
        rel.relationship_type = "spouse"

        with pytest.raises(HTTPException) as exc_info:
            svc._create_relationships([rel], {"t2": 2})
        assert "Invalid relationship: member temp_id not found" in exc_info.value.detail

    def test_invalid_to_temp_id_raises(self, db_session):
        svc = RegistrationService(db_session)
        rel = MagicMock()
        rel.from_temp_id = "t1"
        rel.to_temp_id = "bad"
        rel.relationship_type = "spouse"

        with pytest.raises(HTTPException) as exc_info:
            svc._create_relationships([rel], {"t1": 1})
        assert "Invalid relationship: member temp_id not found" in exc_info.value.detail

    def test_invalid_relationship_type_raises(self, db_session):
        svc = RegistrationService(db_session)
        rel = MagicMock()
        rel.from_temp_id = "t1"
        rel.to_temp_id = "t2"
        rel.relationship_type = "cousin"  # not a valid type

        with pytest.raises(HTTPException) as exc_info:
            svc._create_relationships([rel], {"t1": 1, "t2": 2})
        assert "Invalid relationship type" in exc_info.value.detail

    def test_duplicate_relationship_skipped(self, db_session):
        """Submitting the same relationship twice should not raise — it's silently skipped."""
        from app.models.person import Person

        p1 = Person(first_name="A", last_name="B")
        p2 = Person(first_name="C", last_name="D")
        db_session.add_all([p1, p2])
        db_session.flush()

        svc = RegistrationService(db_session)
        rel = MagicMock()
        rel.from_temp_id = "t1"
        rel.to_temp_id = "t2"
        rel.relationship_type = "spouse"

        # First call should add 2 rows (forward + inverse)
        svc._create_relationships([rel], {"t1": p1.id, "t2": p2.id})
        # Second call with same data — skip duplicate, no error
        svc._create_relationships([rel], {"t1": p1.id, "t2": p2.id})


# ---------------------------------------------------------------------------
# Consent storage (lines 221/231)
# ---------------------------------------------------------------------------


class TestConsentStorage:
    """Test that consent is properly stored during registration."""

    def test_registration_with_consent(self, client, db_session):
        payload = {
            "household_name": "Consent Family",
            "members": [
                {
                    "tempId": "t1",
                    "firstName": "John",
                    "lastName": "Doe",
                }
            ],
            "relationships": [],
            "sacraments": [],
            "consent": {
                "dataPrivacyConsent": True,
                "photoMediaRelease": True,
                "commEmail": True,
                "commSms": False,
                "commPhone": True,
                "termsAcknowledged": True,
            },
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.consent import HouseholdConsent

        consent = (
            db_session.query(HouseholdConsent)
            .filter(HouseholdConsent.data_privacy_consent.is_(True))
            .first()
        )
        assert consent is not None
        assert consent.photo_media_release is True
        assert consent.comm_email is True
        assert consent.comm_sms is False
        assert consent.comm_phone is True
        assert consent.terms_acknowledged is True

    def test_registration_without_consent(self, client, db_session):
        payload = {
            "household_name": "No Consent Family",
            "members": [
                {
                    "tempId": "t1",
                    "firstName": "Jane",
                    "lastName": "Doe",
                }
            ],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        # Verify consent was stored
        from app.models.consent import HouseholdConsent

        consent_count = (
            db_session.query(HouseholdConsent)
            .filter(HouseholdConsent.data_privacy_consent.is_(True))
            .count()
        )
        assert consent_count >= 1


# ---------------------------------------------------------------------------
# _auto_create_births skips (lines 291, 298)
# ---------------------------------------------------------------------------


class TestAutoCreateBirthsSkips:
    """Test the various skip conditions in _auto_create_births."""

    def test_child_without_dob_skipped(self, client, db_session):
        """A child with no date_of_birth should not produce a Birth record."""
        payload = {
            "household_name": "No DOB Family",
            "attendingSince": "2020-01-01",
            "members": [
                {
                    "tempId": "parent-1",
                    "firstName": "Parent",
                    "lastName": "NoDOB",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "child-1",
                    "firstName": "KidNoDOB",
                    "lastName": "NoDOB",
                    # No dateOfBirth
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "parent-1",
                    "toTempId": "child-1",
                    "relationshipType": "parent",
                }
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        births = (
            db_session.query(Birth).filter(Birth.baby_first_name == "KidNoDOB").all()
        )
        assert len(births) == 0

    def test_child_with_dob_before_attending_skipped(self, client, db_session):
        """Child born before attending_since should NOT get a birth record."""
        payload = {
            "household_name": "BeforeAttending",
            "attendingSince": "2023-01-01",
            "members": [
                {
                    "tempId": "p1",
                    "firstName": "Parent",
                    "lastName": "Before",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "c1",
                    "firstName": "OldChild",
                    "lastName": "Before",
                    "dateOfBirth": "2020-06-01",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "p1",
                    "toTempId": "c1",
                    "relationshipType": "parent",
                }
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        births = (
            db_session.query(Birth).filter(Birth.baby_first_name == "OldChild").all()
        )
        assert len(births) == 0

    def test_no_attending_since_skips_births(self, client, db_session):
        """No attending_since → _auto_create_births is never called."""
        payload = {
            "household_name": "NoSince",
            "members": [
                {
                    "tempId": "p1",
                    "firstName": "Parent",
                    "lastName": "NoSince",
                    "isHeadOfHousehold": True,
                },
                {
                    "tempId": "c1",
                    "firstName": "Baby",
                    "lastName": "NoSince",
                    "dateOfBirth": "2024-01-01",
                    "isHeadOfHousehold": False,
                },
            ],
            "relationships": [
                {
                    "fromTempId": "p1",
                    "toTempId": "c1",
                    "relationshipType": "parent",
                }
            ],
            "sacraments": [],
        }
        response = client.post("/api/register", json=payload)
        assert response.status_code == 201

        from app.models.analytics import Birth

        births = db_session.query(Birth).filter(Birth.baby_first_name == "Baby").all()
        assert len(births) == 0


# ---------------------------------------------------------------------------
# get_registration_service dependency (line 371)
# ---------------------------------------------------------------------------


class TestGetRegistrationServiceDependency:
    """Test the FastAPI dependency function."""

    def test_get_registration_service_returns_service(self, db_session):
        svc = get_registration_service(db_session)
        assert isinstance(svc, RegistrationService)
        assert svc.db is db_session
