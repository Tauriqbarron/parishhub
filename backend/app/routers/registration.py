"""API router for public registration endpoint."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.limiter import limiter
from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.person import Gender, Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.models.sacrament import Sacrament, SacramentType
from app.models.settings import Setting
from app.schemas.registration import (
    RegistrationResponse,
    RegistrationSubmission,
    RegistrationURLConfig,
    RegistrationURLResponse,
)
from app.services.relationship import FamilyRelationshipService

router = APIRouter(prefix="/api/register", tags=["registration"])
url_router = APIRouter(prefix="/api/v1/registration", tags=["registration-config"])

REGISTRATION_URL_KEY = "registration_base_url"
REGISTRATION_PATH = "/register"

# Mapping from frontend relationship types to model enum
RELATIONSHIP_TYPE_MAP = {
    "parent": RelationshipType.PARENT,
    "child": RelationshipType.CHILD,
    "spouse": RelationshipType.SPOUSE,
    "sibling": RelationshipType.SIBLING,
}

# Mapping from frontend sacrament types to model enum
SACRAMENT_TYPE_MAP = {
    "baptism": SacramentType.BAPTISM,
    "first_communion": SacramentType.FIRST_COMMUNION,
    "confirmation": SacramentType.CONFIRMATION,
    "marriage": SacramentType.MARRIAGE,
    "holy_orders": SacramentType.HOLY_ORDERS,
    "anointing": SacramentType.ANOINTING,
}

# Sacrament order for validation (earlier sacraments must be created first)
SACRAMENT_ORDER = {
    SacramentType.BAPTISM: 0,
    SacramentType.FIRST_COMMUNION: 1,
    SacramentType.CONFIRMATION: 2,
    SacramentType.MARRIAGE: 3,
    SacramentType.HOLY_ORDERS: 4,
    SacramentType.ANOINTING: 5,
}

logger = logging.getLogger(__name__)

# Mapping from frontend gender to model enum
GENDER_MAP = {
    "male": Gender.MALE,
    "female": Gender.FEMALE,
    "other": Gender.OTHER,
}


@router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit public registration",
)
@limiter.limit("5/minute")
async def submit_registration(
    request: Request,
    data: RegistrationSubmission,
    db: Session = Depends(get_db),
) -> RegistrationResponse:
    """
    Process bulk household registration from public form.

    This endpoint is PUBLIC and does not require authentication.

    Steps:
    1. Create household
    2. Create all persons, mapping temp_id -> real_id
    3. Add persons as household members
    4. Create relationships using the ID mapping
    5. Create sacraments using the ID mapping

    All operations are wrapped in a transaction - if any step fails,
    the entire registration is rolled back.
    """
    try:
        # Step 1: Create household
        household = Household(
            name=data.household_name,
            address_line1=data.street_address,
            city=data.city,
            postal_code=data.postal_code,
        )
        db.add(household)
        db.flush()  # Get household ID

        # Step 2: Create persons and build temp_id -> real_id mapping
        temp_id_to_person_id: dict[str, int] = {}

        for member in data.members:
            # Convert gender string to enum
            gender = None
            if member.gender:
                gender = GENDER_MAP.get(member.gender.lower())

            person = Person(
                first_name=member.first_name,
                middle_name=member.middle_name,
                last_name=member.last_name,
                date_of_birth=member.date_of_birth,
                gender=gender,
                phone=member.phone,
                email=member.email if member.email else None,
            )
            db.add(person)
            db.flush()  # Get person ID

            temp_id_to_person_id[member.temp_id] = person.id

            # Step 3: Add person as household member
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
            db.add(household_member)

        # Step 4: Create relationships (deduplicate to avoid unique constraint violations
        # when frontend sends both directions of a symmetric relationship)
        seen_relationships: set[tuple[int, int, str]] = set()

        for rel in data.relationships:
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

            # Skip if we've already added this pair (forward or inverse)
            if forward_key in seen_relationships:
                continue

            seen_relationships.add(forward_key)
            seen_relationships.add(inverse_key)

            # Create forward relationship
            relationship = FamilyRelationship(
                person_id=from_person_id,
                related_person_id=to_person_id,
                relationship_type=rel_type,
            )
            db.add(relationship)

            # Create inverse relationship
            inverse_relationship = FamilyRelationship(
                person_id=to_person_id,
                related_person_id=from_person_id,
                relationship_type=inverse_type,
            )
            db.add(inverse_relationship)

        # Step 5: Create sacraments (pre-sorted by sacrament order to ensure
        # prerequisite sacraments like baptism are created before dependent ones)
        validated_sacraments = []
        for sac in data.sacraments:
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

            # Validate date is not in the future for most sacraments (except some special cases)
            from datetime import date

            if sac.date > date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Sacrament date '{sac.date}' cannot be in the future for {sac.sacrament_type}",
                )

            validated_sacraments.append((sac, person_id, sac_type))

        # Sort sacraments by type order (baptism first, then first_communion, etc.)
        validated_sacraments.sort(key=lambda x: SACRAMENT_ORDER.get(x[2], 99))

        for sac, person_id, sac_type in validated_sacraments:
            try:
                # Build additional_data with church and minister if provided
                additional_data = (
                    sac.additional_data.copy() if sac.additional_data else {}
                )
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
                db.add(sacrament)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sacrament data for {sac.sacrament_type}: {str(e)}",
                )
            except Exception as e:
                logger.error(
                    f"Error creating sacrament {sac.sacrament_type} for person {person_id}: {str(e)}",
                    exc_info=True,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to create {sac.sacrament_type} record. Please check the data and try again.",
                )

        # Commit all changes
        db.commit()

        return RegistrationResponse(
            household_id=household.id,
            message="Registration submitted successfully",
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again or contact the parish office.",
        )


@url_router.get(
    "/url",
    response_model=RegistrationURLResponse,
    summary="Get registration URL configuration",
)
async def get_registration_url(
    user: Annotated[User, Depends(require_auth)],
    db: Session = Depends(get_db),
) -> RegistrationURLResponse:
    """
    Get the current registration URL configuration.

    Returns the base URL and full registration URL for QR code generation.
    Requires authentication.
    """
    setting = db.query(Setting).filter(Setting.key == REGISTRATION_URL_KEY).first()

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registration URL not configured. Please set a base URL first.",
        )

    base_url = setting.value.rstrip("/")
    registration_url = f"{base_url}{REGISTRATION_PATH}"

    return RegistrationURLResponse(
        base_url=base_url,
        registration_url=registration_url,
    )


@url_router.put(
    "/url",
    response_model=RegistrationURLResponse,
    summary="Update registration URL configuration",
)
async def update_registration_url(
    config: RegistrationURLConfig,
    user: Annotated[User, Depends(require_auth)],
    db: Session = Depends(get_db),
) -> RegistrationURLResponse:
    """
    Update the base URL for public registration.

    This URL is used for QR code generation (e.g., Cloudflare tunnel URL).
    Requires authentication.
    """
    base_url = config.base_url.rstrip("/")

    setting = db.query(Setting).filter(Setting.key == REGISTRATION_URL_KEY).first()

    if setting:
        setting.value = base_url
    else:
        setting = Setting(key=REGISTRATION_URL_KEY, value=base_url)
        db.add(setting)

    db.commit()

    registration_url = f"{base_url}{REGISTRATION_PATH}"

    return RegistrationURLResponse(
        base_url=base_url,
        registration_url=registration_url,
    )
