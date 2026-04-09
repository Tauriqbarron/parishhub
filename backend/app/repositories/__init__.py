"""Repository layer — database abstraction protocols and implementations."""

from app.repositories.death import (
    DeathRepository,
    SqlAlchemyDeathRepository,
)
from app.repositories.household import (
    HouseholdRepository,
    SqlAlchemyHouseholdRepository,
)
from app.repositories.mass_time import (
    MassTimeRepository,
    SqlAlchemyMassTimeRepository,
)
from app.repositories.person import (
    FakePersonRepository,
    PersonRepository,
    SqlAlchemyPersonRepository,
)
from app.repositories.relationship import (
    RelationshipRepository,
    SqlAlchemyRelationshipRepository,
)
from app.repositories.sacrament import (
    FakeSacramentRepository,
    SacramentRepository,
    SqlAlchemySacramentRepository,
)

__all__ = [
    # Person repositories
    "PersonRepository",
    "SqlAlchemyPersonRepository",
    "FakePersonRepository",
    # Sacrament repositories
    "SacramentRepository",
    "SqlAlchemySacramentRepository",
    "FakeSacramentRepository",
    # Death repositories
    "DeathRepository",
    "SqlAlchemyDeathRepository",
    # Household repositories
    "HouseholdRepository",
    "SqlAlchemyHouseholdRepository",
    # MassTime repositories
    "MassTimeRepository",
    "SqlAlchemyMassTimeRepository",
    # Relationship repositories
    "RelationshipRepository",
    "SqlAlchemyRelationshipRepository",
]
