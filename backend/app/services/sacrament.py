"""Service layer for Sacrament operations (DIP compliant).

SacramentService implements the domain logic and validation rules for
sacraments while delegating all persistence concerns to SacramentRepository.
This satisfies the Dependency Inversion Principle — the service depends on
an abstraction (protocol), not on SQLAlchemy or any specific ORM.
"""

from datetime import date
from typing import Any, Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.person import Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.models.sacrament import Sacrament, SacramentType
from app.database import get_db
from app.repositories.sacrament import (
    SacramentRepository,
    SqlAlchemySacramentRepository,
)
from app.schemas.sacrament import (
    MarriageSideEffects,
    SacramentCreate,
    SacramentUpdate,
)


class SacramentValidationError(Exception):
    """Exception raised for sacrament validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SacramentService:
    """Service class for Sacrament CRUD operations with domain validation.

    The service enforces canonical Catholic sacrament ordering rules
    and handles marriage side effects (spouse relationship + household creation).
    All sacrament persistence is delegated to a SacramentRepository implementation.
    Direct DB access is retained ONLY for household/family-relationship side effects
    (which have not yet been moved to their own repositories).
    """

    def __init__(self, repo: SacramentRepository, db: Session):
        self.repo = repo
        self.db = db
        self.last_marriage_effects: Optional[MarriageSideEffects] = None

    # -----------------------------------------------------------------
    # Private helpers — domain logic only, no DB access
    # -----------------------------------------------------------------
    def _get_person_sacraments(self, person_id: int) -> dict[SacramentType, Sacrament]:
        """Index sacraments by type for a person (reads from repository)."""
        return self.repo.get_sacraments_by_person(person_id)

    def _validate_sacrament_order(
        self,
        person_id: int,
        sacrament_type: SacramentType,
        date_received: date,
        exclude_sacrament_id: Optional[int] = None,
    ) -> None:
        """Enforce canonical Catholic sacrament ordering rules.

        The Church's canonical order of initiation sacraments is:
          1. Baptism  (required before all others)
          2. First Communion  (requires prior Baptism)
          3. Confirmation  (requires prior Baptism; typically after First Communion)

        Marriage is the only repeatable sacrament — a Catholic may remarry
        after a spouse's death (or after an annulment, which is tracked
        separately and outside the scope of this model).
        """
        existing = self._get_person_sacraments(person_id)

        # --- Baptism back-date guard (BEFORE duplicate check) -----------
        # If Baptism is added after First Communion or Confirmation records
        # already exist (e.g. correcting a missing record), ensure the Baptism
        # date does not post-date the dependent sacraments.  This check runs
        # before the duplicate guard so that date violations surface first,
        # guiding users to enter historically correct dates.
        # NOTE: Check Confirmation FIRST so its error message appears when
        # both FirstCommunion and Confirmation exist (more informative).
        if sacrament_type == SacramentType.BAPTISM:
            if SacramentType.CONFIRMATION in existing:
                confirmation = existing[SacramentType.CONFIRMATION]
                if date_received > confirmation.date_received:
                    raise SacramentValidationError(
                        "Baptism date must be before Confirmation date"
                    )
            if SacramentType.FIRST_COMMUNION in existing:
                first_communion = existing[SacramentType.FIRST_COMMUNION]
                if date_received > first_communion.date_received:
                    raise SacramentValidationError(
                        "Baptism date must be before First Communion date"
                    )

        # --- Duplicate guard ---------------------------------------------
        # All sacraments are received once in a lifetime, except Marriage
        # (CIC can. 1141 — a valid sacramental marriage is indissoluble, but
        # a new marriage is permitted after the death of a spouse).
        if sacrament_type != SacramentType.MARRIAGE:
            if sacrament_type in existing:
                existing_sacrament = existing[sacrament_type]
                # If we're updating the same sacrament, it's okay
                if (
                    exclude_sacrament_id
                    and existing_sacrament.id == exclude_sacrament_id
                ):
                    # Editing the same record — not a true duplicate.
                    pass
                else:
                    raise SacramentValidationError(
                        f"This person already has a {sacrament_type.value} record"
                    )

        # --- First Communion ordering -----------------------------------
        # CIC can. 913 §1: First Communion presupposes prior Baptism and at
        # least some knowledge of the faith.  We enforce only the date ordering
        # here; catechetical readiness is not tracked in this system.
        if sacrament_type == SacramentType.FIRST_COMMUNION:
            if SacramentType.BAPTISM in existing:
                baptism = existing[SacramentType.BAPTISM]
                if date_received < baptism.date_received:
                    raise SacramentValidationError(
                        "First Communion date must be after Baptism date"
                    )

        # --- Confirmation ordering --------------------------------------
        # CIC can. 842 §2: Baptism, Confirmation, and Eucharist form the
        # sacraments of Christian initiation and are interrelated.  Confirmation
        # may not precede Baptism or (by diocesan norm) First Communion.
        if sacrament_type == SacramentType.CONFIRMATION:
            # Check Baptism date first — fundamental requirement
            if SacramentType.BAPTISM in existing:
                baptism = existing[SacramentType.BAPTISM]
                if date_received < baptism.date_received:
                    raise SacramentValidationError(
                        "Confirmation date must be after Baptism date"
                    )
            # Then verify First Communion was received
            if SacramentType.FIRST_COMMUNION not in existing:
                raise SacramentValidationError(
                    "Confirmation may only be received after First Communion"
                )
            first_communion = existing[SacramentType.FIRST_COMMUNION]
            if date_received < first_communion.date_received:
                raise SacramentValidationError(
                    "Confirmation date must be after First Communion date"
                )

    # -----------------------------------------------------------------
    # Public API — domain operations (no raw DB touches)
    # -----------------------------------------------------------------
    def create(self, sacrament_data: SacramentCreate) -> Sacrament:
        """Create a new sacrament record with validation and marriage side effects.

        Business rules enforced:
        - Person must exist
        - Sacrament order rules (via _validate_sacrament_order)
        - Marriage creates spouse relationship + household automatically
        """
        # Validate person exists
        person = self.db.get(Person, sacrament_data.person_id)
        if person is None:
            raise SacramentValidationError(
                f"Person with id {sacrament_data.person_id} not found"
            )

        # Handle backward-compatibility: extract spouse_id from additional_data
        # if not set as top-level field (tests send it nested in additional_data)
        extra_data = {}
        if sacrament_data.model_extra:
            extra_data = sacrament_data.model_extra
        spouse_id = (
            sacrament_data.spouse_id
            or extra_data.get("additional_data", {}).get("spouse_id")
            if isinstance(extra_data.get("additional_data"), dict)
            else None
        )

        # Validate sacrament order before persisting
        self._validate_sacrament_order(
            person.id,
            sacrament_data.sacrament_type,
            sacrament_data.date_received,
        )

        # Persist via repository
        sacrament = self.repo.create(sacrament_data)
        self.last_marriage_effects = None

        # Marriage side effects: spouse relationship + household
        if sacrament_data.sacrament_type == SacramentType.MARRIAGE:
            self.last_marriage_effects = self._handle_marriage_side_effects(
                person, sacrament, spouse_id
            )

        return sacrament

    def _handle_marriage_side_effects(
        self, person: Person, sacrament: Sacrament, spouse_id: Optional[int]
    ) -> MarriageSideEffects:
        """Handle automatic side effects when a marriage is recorded."""
        effects = MarriageSideEffects()

        if spouse_id is None:
            effects.household_deferred = True
            return effects

        spouse = self.repo.get_by_id(spouse_id)
        if spouse is None:
            effects.household_deferred = True
            return effects

        # -----------------------------------------------------------------
        # 1) Spouse relationship (bidirectional)
        # -----------------------------------------------------------------
        from sqlalchemy import select

        existing = self.db.execute(
            select(FamilyRelationship).where(
                FamilyRelationship.person_id == person.id,
                FamilyRelationship.related_person_id == spouse_id,
                FamilyRelationship.relationship_type == RelationshipType.SPOUSE,
            )
        ).scalar_one_or_none()

        if existing is None:
            # Create bidirectional spouse relationship — direct DB session access
            # needed because FamilyRelationship is not a sacrament and has no repo yet.
            # This is a pragmatic compromise until RelationshipService gets its own repository.
            rel = FamilyRelationship(
                person_id=person.id,
                related_person_id=spouse_id,
                relationship_type=RelationshipType.SPOUSE,
            )
            inverse = FamilyRelationship(
                person_id=spouse_id,
                related_person_id=person.id,
                relationship_type=RelationshipType.SPOUSE,
            )
            self.db.add(rel)
            self.db.add(inverse)
            self.db.flush()
            effects.spouse_relationship_created = True

        # -----------------------------------------------------------------
        # 2) Household creation
        # -----------------------------------------------------------------
        if person.last_name == spouse.last_name:
            household_name = f"The {person.last_name} Family"
        else:
            household_name = f"{person.last_name} & {spouse.last_name} Family"

        household = Household(
            name=household_name,
            origin_sacrament_id=sacrament.id,
        )
        self.db.add(household)
        self.db.flush()

        head_member = HouseholdMember(
            household_id=household.id,
            person_id=person.id,
            role=HouseholdRole.HEAD,
            is_primary_household=True,
        )
        spouse_member = HouseholdMember(
            household_id=household.id,
            person_id=spouse_id,
            role=HouseholdRole.SPOUSE,
            is_primary_household=True,
        )
        self.db.add(head_member)
        self.db.add(spouse_member)

        # Remove both from parent households (where role=CHILD)
        self.db.execute(
            HouseholdMember.__table__.delete().where(
                HouseholdMember.person_id == person.id,
                HouseholdMember.role == HouseholdRole.CHILD,
            )
        )
        self.db.execute(
            HouseholdMember.__table__.delete().where(
                HouseholdMember.person_id == spouse_id,
                HouseholdMember.role == HouseholdRole.CHILD,
            )
        )

        sacrament.notes = (sacrament.notes or "") + " [Auto-created household]"
        self.db.commit()

        effects.household_id = household.id
        effects.household_name = household_name
        effects.household_created = True

        return effects

    # -----------------------------------------------------------------
    # Query methods — thin wrappers over repository
    # -----------------------------------------------------------------
    def get_by_id(self, sacrament_id: int) -> Optional[Sacrament]:
        return self.repo.get_by_id(sacrament_id)

    def get_by_id_with_person(self, sacrament_id: int) -> Optional[Sacrament]:
        return self.repo.get_by_id_with_person(sacrament_id)

    def get_by_person(self, person_id: int) -> list[Sacrament]:
        return self.repo.get_by_person(person_id)

    def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        person_id: Optional[int] = None,
        sacrament_type: Optional[SacramentType] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        sort_by: str = "date_received",
        sort_order: str = "desc",
    ) -> tuple[list[Sacrament], int]:
        return self.repo.get_list(
            page=page,
            per_page=per_page,
            person_id=person_id,
            sacrament_type=sacrament_type,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def update(
        self, sacrament_id: int, sacrament_data: SacramentUpdate
    ) -> Optional[Sacrament]:
        """Update a sacrament with order validation on type/date changes."""
        existing = self.repo.get_by_id(sacrament_id)
        if existing is None:
            return None

        update_data = sacrament_data.model_dump(exclude_unset=True)
        new_type = update_data.get("sacrament_type", existing.sacrament_type)
        new_date = update_data.get("date_received", existing.date_received)

        if "sacrament_type" in update_data or "date_received" in update_data:
            self._validate_sacrament_order(
                existing.person_id,
                new_type,
                new_date,
                exclude_sacrament_id=sacrament_id,
            )

        return self.repo.update(sacrament_id, sacrament_data)

    def delete(self, sacrament_id: int) -> bool:
        return self.repo.delete(sacrament_id)

    def get_statistics(self) -> dict[str, Any]:
        return self.repo.get_statistics()


def get_sacrament_service(db: Session = Depends(get_db)) -> SacramentService:
    """FastAPI dependency that returns a SacramentService with SQLAlchemy repo."""
    return SacramentService(SqlAlchemySacramentRepository(db), db)
