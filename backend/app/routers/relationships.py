"""API router for FamilyRelationship operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import User, require_auth
from app.database import get_db
from app.models.relationship import RelationshipType
from app.schemas.relationship import FamilyRelationshipCreate, FamilyRelationshipResponse
from app.services.relationship import FamilyRelationshipService

router = APIRouter(tags=["relationships"])


def get_relationship_service(db: Session = Depends(get_db)) -> FamilyRelationshipService:
    """Dependency to get FamilyRelationshipService instance."""
    return FamilyRelationshipService(db)


class CreateRelationshipRequest(BaseModel):
    """Request body for creating a relationship."""

    related_person_id: int
    relationship_type: RelationshipType


class FamilyMember(BaseModel):
    """A family member in the family tree response."""

    id: int
    first_name: str
    middle_name: str | None = None
    last_name: str
    relationship_id: int


class FamilyTreeResponse(BaseModel):
    """Response for family tree endpoint."""

    parents: list[FamilyMember]
    children: list[FamilyMember]
    spouse: FamilyMember | None
    siblings: list[FamilyMember]


# Endpoints under /api/persons/{id}
persons_router = APIRouter(prefix="/api/persons", tags=["persons"])


@persons_router.post(
    "/{person_id}/relationships",
    response_model=FamilyRelationshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a relationship between two people",
)
async def create_relationship(
    person_id: int,
    relationship_data: CreateRelationshipRequest,
    service: Annotated[FamilyRelationshipService, Depends(get_relationship_service)],
    user: Annotated[User, Depends(require_auth)],
) -> FamilyRelationshipResponse:
    """
    Create a family relationship from person_id to another person.

    The inverse relationship is automatically created:
    - If A is parent of B, B becomes child of A
    - If A is spouse of B, B becomes spouse of A
    - If A is sibling of B, B becomes sibling of A
    """
    # Check if person exists
    if not service.person_exists(person_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    # Check if related person exists
    if not service.person_exists(relationship_data.related_person_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Related person not found",
        )

    # Check if they're the same person
    if person_id == relationship_data.related_person_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create relationship with self",
        )

    # Check if relationship already exists
    if service.relationship_exists(person_id, relationship_data.related_person_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Relationship already exists between these people",
        )

    create_data = FamilyRelationshipCreate(
        person_id=person_id,
        related_person_id=relationship_data.related_person_id,
        relationship_type=relationship_data.relationship_type,
    )
    relationship = service.create(create_data)
    return FamilyRelationshipResponse.model_validate(relationship)


@persons_router.get(
    "/{person_id}/relationships",
    response_model=list[FamilyRelationshipResponse],
    summary="Get all relationships for a person",
)
async def get_relationships(
    person_id: int,
    service: Annotated[FamilyRelationshipService, Depends(get_relationship_service)],
    user: Annotated[User, Depends(require_auth)],
) -> list[FamilyRelationshipResponse]:
    """
    Get all family relationships for a person.
    """
    if not service.person_exists(person_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    relationships = service.get_relationships_for_person(person_id)
    return [FamilyRelationshipResponse.model_validate(r) for r in relationships]


@persons_router.get(
    "/{person_id}/family-tree",
    response_model=FamilyTreeResponse,
    summary="Get family tree for a person",
)
async def get_family_tree(
    person_id: int,
    service: Annotated[FamilyRelationshipService, Depends(get_relationship_service)],
    user: Annotated[User, Depends(require_auth)],
) -> FamilyTreeResponse:
    """
    Get the full family tree for a person.

    Returns structured data with:
    - parents
    - children
    - spouse
    - siblings
    """
    if not service.person_exists(person_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    tree = service.get_family_tree(person_id)
    return FamilyTreeResponse(**tree)


# Standalone endpoint for deleting relationships
@router.delete(
    "/api/relationships/{relationship_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a relationship",
)
async def delete_relationship(
    relationship_id: int,
    service: Annotated[FamilyRelationshipService, Depends(get_relationship_service)],
    user: Annotated[User, Depends(require_auth)],
) -> None:
    """
    Delete a family relationship.

    This also deletes the inverse relationship.
    """
    deleted = service.delete(relationship_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found",
        )
