"""Registration service for processing public registration forms."""

import logging
from datetime import date
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.mappings import (
    GENDER_MAP,
    RELATIONSHIP_TYPE_MAP,
    SACRAMENT_TYPE_MAP,
)
from app.models.analytics import Birth
from app.models.consent import HouseholdConsent
from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.person import Person
from app.models.relationship import FamilyRelationship
from app.models.sacrament import Sacrament, SacramentType
from app.models.settings import Setting
from app.schemas.registration import (
    IndividualRegistrationResponse,
    IndividualRegistrationSubmission,
    RegistrationResponse,
    RegistrationSubmission,
)
from app.services.relationship import FamilyRelationshipService

logger = logging.getLogger(__name__)

REGISTRATION_URL_KEY = "registration_base_url"
REGISTRATION_PATH = "/register"

# Sacrament order for validation (earlier sacraments must be created first)
SACRAMENT_ORDER = {
    SacramentType.BAPTISM: 0,
    SacramentType.FIRST_COMMUNION: 1,
    SacramentType.CONFIRMATION: 2,
    SacramentType.MARRIAGE: 3,
    SacramentType.HOLY_ORDERS: 4,
    SacramentType.ANOINTING: 5,
}


class RegistrationService:
    """Business logic for public registration processing."""

    def __init__(self, db: Session):
        self.db = db

    def _get_request_ip(self, request: Optional[Request]) -> Optional[str]:
        return request.client.host if request and request.client else None

    def _create_person(self, member) -> Person:
        gender = GENDER_MAP.get(member.gender.lower()) if member.gender else None
        person = Person(
            first_name=member.first_name,
            middle_name=member.middle_name,
            last_name=member.last_name,
            date_of_birth=member.date_of_birth,
            gender=gender,
            phone=member.phone,
            email=member.email or None,
        )
        self.db.add(person)
        self.db.flush()
        return person

    def _create_relationships(
        self, data_relationships, temp_id_to_person_id: dict[str, int]
    ):
        """Create family relationships, deduplicating symmetric pairs."""
        seen_relationships: set[tuple[int, int, str]] = set()

        for rel in data_relationships:
            from_person_id = temp_id_to_person_id.get(rel.from_temp_id)
            to_person_id = temp_id_to_person_id.get(rel.to_temp_id)

            if not from_person_id or not to_person_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid relationship: member temp_id not found",
                )

            rel_type = RELATIONSHIP_TYPE_MAP.get(rel.relationship_type.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid relationship type: {rel.relationship_type}",
                )

            inverse_type = FamilyRelationshipService.INVERSE_RELATIONSHIPS[rel_type]
            forward_key = (from_person_id, to_person_id, rel_type.value)
            inverse_key = (to_person_id, from_person_id, inverse_type.value)

            if forward_key in seen_relationships:
                continue

            seen_relationships.add(forward_key)
            seen_relationships.add(inverse_key)

            self.db.add(
                FamilyRelationship(
                    person_id=from_person_id,
                    related_person_id=to_person_id,
                    relationship_type=rel_type,
                )
            )
            self.db.add(
                FamilyRelationship(
                    person_id=to_person_id,
                    related_person_id=from_person_id,
                    relationship_type=inverse_type,
                )
            )

    def _validate_and_build_sacraments(
        self,
        sacraments,
        temp_id_to_person_id: dict[str, int],
        individual_person_id: Optional[int] = None,
    ) -> list[tuple]:
        """Validate sacrament data and return list of (sacrament_data, person_id, sac_type)."""
        validated = []
        for sac in sacraments:
            if individual_person_id is not None:
                person_id = individual_person_id
            else:
                person_id = temp_id_to_person_id.get(sac.member_temp_id)
                if not person_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid sacrament: member temp_id '{sac.member_temp_id}' not found. Available temp_ids: {list(temp_id_to_person_id.keys())}",
                    )

            if not sac.sacrament_type or not sac.sacrament_type.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Sacrament type cannot be empty",
                )

            sac_type = SACRAMENT_TYPE_MAP.get(sac.sacrament_type.lower().strip())
            if not sac_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sacrament type: '{sac.sacrament_type}'. Valid types: {list(SACRAMENT_TYPE_MAP.keys())}",
                )

            if not sac.date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sacrament date is required for {sac.sacrament_type}",
                )

            if sac.date > date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sacrament date '{sac.date}' cannot be in the future for {sac.sacrament_type}",
                )

            validated.append((sac, person_id, sac_type))

        validated.sort(key=lambda x: SACRAMENT_ORDER.get(x[2], 99))
        return validated

    def _create_sacrament_records(self, validated_sacraments: list[tuple]):
        """Create Sacrament records from validated data."""
        for sac, person_id, sac_type in validated_sacraments:
            additional_data = sac.additional_data.copy() if sac.additional_data else {}
            if sac.church:
                if not sac.church.strip():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Church name cannot be empty for {sac.sacrament_type}",
                    )
                additional_data["church"] = sac.church.strip()
            if sac.minister:
                if not sac.minister.strip():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Minister name cannot be empty for {sac.sacrament_type}",
                    )
                additional_data["minister"] = sac.minister.strip()

            sacrament = Sacrament(
                person_id=person_id,
                sacrament_type=sac_type,
                date_received=sac.date,
                additional_data=additional_data if additional_data else None,
            )
            self.db.add(sacrament)

    def register(
        self, data: RegistrationSubmission, request: Optional[Request] = None
    ) -> RegistrationResponse:
        """Process bulk household registration from public form."""
        # Step 1: Create household
        household = Household(
            name=data.household_name,
            address_line1=data.street_address,
            city=data.city,
            postal_code=data.postal_code,
            attending_since=data.attending_since,
        )
        self.db.add(household)
        self.db.flush()

        # Step 1b: Store consent if provided
        if data.consent:
            consent_record = HouseholdConsent(
                household_id=household.id,
                data_privacy_consent=data.consent.data_privacy_consent,
                photo_media_release=data.consent.photo_media_release,
                comm_email=data.consent.comm_email,
                comm_sms=data.consent.comm_sms,
                comm_phone=data.consent.comm_phone,
                terms_acknowledged=data.consent.terms_acknowledged,
                ip_address=self._get_request_ip(request),
            )
            self.db.add(consent_record)

        # Step 2: Create persons and build temp_id -> real_id mapping
        temp_id_to_person_id: dict[str, int] = {}

        for member in data.members:
            person = self._create_person(member)
            temp_id_to_person_id[member.temp_id] = person.id

            # Step 3: Add person as household member
            if member.lives_in_household:
                role = (
                    HouseholdRole.HEAD
                    if member.is_head_of_household
                    else HouseholdRole.OTHER
                )
                household_member = HouseholdMember(
                    household_id=household.id,
                    person_id=person.id,
                    role=role,
                    is_primary_household=True,
                )
                self.db.add(household_member)

        # Step 4: Create relationships
        self._create_relationships(data.relationships, temp_id_to_person_id)

        # Step 5: Create sacraments
        validated_sacraments = self._validate_and_build_sacraments(
            data.sacraments, temp_id_to_person_id
        )
        self._create_sacrament_records(validated_sacraments)

        # Step 6: Auto-create birth records for children born during parish tenure
        if data.attending_since:
            self._auto_create_births(data, temp_id_to_person_id)

        return RegistrationResponse(
            household_id=household.id,
            message="Registration submitted successfully",
        )

    def _auto_create_births(
        self, data: RegistrationSubmission, temp_id_to_person_id: dict[str, int]
    ):
        """Create birth records for children born during parish tenure."""
        child_parents: dict[str, list[str]] = {}
        for rel in data.relationships:
            if rel.relationship_type.lower() == "parent":
                child_tid = rel.to_temp_id
                parent_tid = rel.from_temp_id
                if child_tid not in child_parents:
                    child_parents[child_tid] = []
                child_parents[child_tid].append(parent_tid)

        for child_temp_id, parent_temp_ids in child_parents.items():
            child_member = next(
                (m for m in data.members if m.temp_id == child_temp_id), None
            )
            if not child_member or not child_member.date_of_birth:
                continue

            if child_member.date_of_birth < data.attending_since:
                continue

            child_person_id = temp_id_to_person_id.get(child_temp_id)
            if not child_person_id:
                continue

            resolved_parent_ids = []
            for ptid in parent_temp_ids:
                pid = temp_id_to_person_id.get(ptid)
                if pid:
                    resolved_parent_ids.append(pid)

            birth_record = Birth(
                baby_first_name=child_member.first_name,
                baby_last_name=child_member.last_name,
                date_of_birth=child_member.date_of_birth,
                parent1_id=resolved_parent_ids[0]
                if len(resolved_parent_ids) > 0
                else None,
                parent2_id=resolved_parent_ids[1]
                if len(resolved_parent_ids) > 1
                else None,
                notes="Auto-recorded during family registration",
            )
            self.db.add(birth_record)

    def register_individual(
        self, data: IndividualRegistrationSubmission
    ) -> IndividualRegistrationResponse:
        """Process individual registration from public form (no household)."""
        # Step 1: Create person
        gender = GENDER_MAP.get(data.gender.lower()) if data.gender else None
        person = Person(
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=gender,
            phone=data.phone,
            email=data.email or None,
        )
        self.db.add(person)
        self.db.flush()

        # Step 2: Create sacraments
        validated_sacraments = self._validate_and_build_sacraments(
            data.sacraments, {}, individual_person_id=person.id
        )
        self._create_sacrament_records(validated_sacraments)

        return IndividualRegistrationResponse(
            person_id=person.id,
            message="Registration submitted successfully",
        )

    def get_registration_url(self) -> str:
        """Get the full registration URL from settings."""
        setting = (
            self.db.query(Setting).filter(Setting.key == REGISTRATION_URL_KEY).first()
        )
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration URL not configured. Please set a base URL first.",
            )
        base_url = setting.value.rstrip("/")
        return f"{base_url}{REGISTRATION_PATH}"


def get_registration_service(db: Session = Depends(get_db)) -> RegistrationService:
    """FastAPI dependency for RegistrationService."""
    return RegistrationService(db)
