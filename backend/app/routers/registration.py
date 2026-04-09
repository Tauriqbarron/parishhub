"""API router for public registration endpoint."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth import User, require_auth
from app.limiter import limiter
from app.schemas.registration import (
    IndividualRegistrationResponse,
    IndividualRegistrationSubmission,
    RegistrationResponse,
    RegistrationSubmission,
    RegistrationURLConfig,
    RegistrationURLResponse,
)
from app.services.registration import RegistrationService, get_registration_service

router = APIRouter(prefix="/api/register", tags=["registration"])
url_router = APIRouter(prefix="/api/v1/registration", tags=["registration-config"])

logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit public registration",
)
@limiter.limit("60/minute")
async def submit_registration(
    request: Request,
    data: RegistrationSubmission,
    service: Annotated[RegistrationService, Depends(get_registration_service)],
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
        result = service.register(data, request=request)
        service.db.commit()
        return result
    except HTTPException:
        service.db.rollback()
        raise
    except Exception as e:
        service.db.rollback()
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again or contact the parish office.",
        )


@router.post(
    "/individual",
    response_model=IndividualRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit individual registration (no household)",
)
@limiter.limit("60/minute")
async def submit_individual_registration(
    request: Request,
    data: IndividualRegistrationSubmission,
    service: Annotated[RegistrationService, Depends(get_registration_service)],
) -> IndividualRegistrationResponse:
    """
    Process individual registration from public form (no household).

    This endpoint is PUBLIC and does not require authentication.

    Steps:
    1. Create person
    2. Create sacraments
    3. Store consent (if provided)

    All operations are wrapped in a transaction.
    """
    try:
        result = service.register_individual(data)
        service.db.commit()
        return result
    except HTTPException:
        service.db.rollback()
        raise
    except Exception as e:
        service.db.rollback()
        logger.error(f"Individual registration failed: {str(e)}", exc_info=True)
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
    service: Annotated[RegistrationService, Depends(get_registration_service)],
) -> RegistrationURLResponse:
    """
    Get the current registration URL configuration.

    Returns the base URL and full registration URL for QR code generation.
    Requires authentication.
    """
    registration_url = service.get_registration_url()
    return RegistrationURLResponse(
        base_url=registration_url.rsplit("/register", 1)[0],
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
    service: Annotated[RegistrationService, Depends(get_registration_service)],
) -> RegistrationURLResponse:
    """
    Update the base URL for public registration.

    This URL is used for QR code generation (e.g., Cloudflare tunnel URL).
    Requires authentication.
    """
    return service.update_registration_url(config.base_url)
