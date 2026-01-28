"""API router for public registration endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
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

# Inverse relationships for bidirectional creation
INVERSE_RELATIONSHIPS = {
    RelationshipType.PARENT: RelationshipType.CHILD,
    RelationshipType.CHILD: RelationshipType.PARENT,
    RelationshipType.SPOUSE: RelationshipType.SPOUSE,
    RelationshipType.SIBLING: RelationshipType.SIBLING,
}

# Mapping from frontend sacrament types to model enum
SACRAMENT_TYPE_MAP = {
    "baptism": SacramentType.BAPTISM,
    "first_communion": SacramentType.FIRST_COMMUNION,
    "confirmation": SacramentType.CONFIRMATION,
    "marriage": SacramentType.MARRIAGE,
    "holy_orders": SacramentType.HOLY_ORDERS,
}

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
async def submit_registration(
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
            role = HouseholdRole.HEAD if member.is_head_of_household else HouseholdRole.OTHER
            household_member = HouseholdMember(
                household_id=household.id,
                person_id=person.id,
                role=role,
                is_primary_household=True,
            )
            db.add(household_member)

        # Step 4: Create relationships
        for rel in data.relationships:
            from_person_id = temp_id_to_person_id.get(rel.from_temp_id)
            to_person_id = temp_id_to_person_id.get(rel.to_temp_id)

            if not from_person_id or not to_person_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid relationship: member temp_id not found",
                )

            rel_type = RELATIONSHIP_TYPE_MAP.get(rel.relationship_type.lower())
            if not rel_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid relationship type: {rel.relationship_type}",
                )

            # Create forward relationship
            relationship = FamilyRelationship(
                person_id=from_person_id,
                related_person_id=to_person_id,
                relationship_type=rel_type,
            )
            db.add(relationship)

            # Create inverse relationship
            inverse_type = INVERSE_RELATIONSHIPS[rel_type]
            inverse_relationship = FamilyRelationship(
                person_id=to_person_id,
                related_person_id=from_person_id,
                relationship_type=inverse_type,
            )
            db.add(inverse_relationship)

        # Step 5: Create sacraments
        for sac in data.sacraments:
            person_id = temp_id_to_person_id.get(sac.member_temp_id)

            if not person_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sacrament: member temp_id not found",
                )

            sac_type = SACRAMENT_TYPE_MAP.get(sac.sacrament_type.lower())
            if not sac_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid sacrament type: {sac.sacrament_type}",
                )

            # Build additional_data with church and minister if provided
            additional_data = sac.additional_data.copy() if sac.additional_data else {}
            if sac.church:
                additional_data["church"] = sac.church
            if sac.minister:
                additional_data["minister"] = sac.minister

            # Only create sacrament if we have a date
            if sac.date:
                sacrament = Sacrament(
                    person_id=person_id,
                    sacrament_type=sac_type,
                    date_received=sac.date,
                    additional_data=additional_data if additional_data else None,
                )
                db.add(sacrament)

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
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
