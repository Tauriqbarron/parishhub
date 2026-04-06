"""Centralised mappings from string keys to enum values.

Auto-generated from enum values — no manual maintenance needed.
"""

from app.models.person import Gender
from app.models.relationship import RelationshipType
from app.models.sacrament import SacramentType

GENDER_MAP: dict[str, Gender] = {e.value: e for e in Gender}
RELATIONSHIP_TYPE_MAP: dict[str, RelationshipType] = {
    e.value: e for e in RelationshipType
}
SACRAMENT_TYPE_MAP: dict[str, SacramentType] = {e.value: e for e in SacramentType}
