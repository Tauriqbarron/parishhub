from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.relationship import RelationshipType


class FamilyRelationshipBase(BaseModel):
    """Base schema for FamilyRelationship."""

    person_id: int
    related_person_id: int
    relationship_type: RelationshipType


class FamilyRelationshipCreate(FamilyRelationshipBase):
    """Schema for creating a new FamilyRelationship."""

    pass


class FamilyRelationshipUpdate(BaseModel):
    """Schema for updating an existing FamilyRelationship."""

    relationship_type: Optional[RelationshipType] = None


class FamilyRelationshipResponse(FamilyRelationshipBase):
    """Schema for FamilyRelationship response including database fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
