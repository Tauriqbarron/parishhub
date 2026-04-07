"""Service layer for Sacrament operations."""

from datetime import date
from typing import Any, Optional

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.person import Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.models.sacrament import Sacrament, SacramentType
from app.schemas.sacrament import (
    MarriageSideEffects,
    SacramentCreate,
    SacramentUpdate,
)
from app.utils.pagination import paginate


class SacramentValidationError(Exception):
    """Exception raised for sacrament validation errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class SacramentService:
    """Service class for Sacrament CRUD operations."""

    def __init__(self, db: Session):
        self.db = db
        self.last_marriage_effects: Optional[MarriageSideEffects] = None

    def _get_person_sacraments(self, person_id: int) -> dict[SacramentType, Sacrament]:
        """Get all sacraments for a person indexed by type."""
        stmt = select(Sacrament).where(Sacrament.person_id == person_id)
        sacraments = self.db.execute(stmt).scalars().all()
        return {s.sacrament_type: s for s in sacraments}

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

    def create(self, sacrament_data: SacramentCreate) -> Sacrament:
        """Create a new sacrament record. Returns sacrament. Use get_last_marriage_effects() for marriage side effects."""
        # Validate person exists
        person = self.db.get(Person, sacrament_data.person_id)
        if not person:
            raise SacramentValidationError(
                f"Person with id {sacrament_data.person_id} not found"
            )

        # Validate sacrament order
        self._validate_sacrament_order(
            sacrament_data.person_id,
            sacrament_data.sacrament_type,
            sacrament_data.date_received,
        )

        sacrament = Sacrament(**sacrament_data.model_dump())
        self.db.add(sacrament)
        self.db.flush()

        self.last_marriage_effects = None
        if sacrament_data.sacrament_type == SacramentType.MARRIAGE:
            self.last_marriage_effects = self._handle_marriage_side_effects(
                person, sacrament
            )

        self.db.commit()
        self.db.refresh(sacrament)
        return sacrament

    def _handle_marriage_side_effects(
        self, person: Person, sacrament: Sacrament
    ) -> MarriageSideEffects:
        """Handle automatic side effects when a marriage is recorded."""
        spouse_id = sacrament.spouse_id
        effects = MarriageSideEffects()

        if spouse_id:
            spouse = self.db.get(Person, spouse_id)
            if spouse:
                # Check if spouse relationship already exists
                existing = self.db.execute(
                    select(FamilyRelationship).where(
                        FamilyRelationship.person_id == person.id,
                        FamilyRelationship.related_person_id == spouse_id,
                        FamilyRelationship.relationship_type == RelationshipType.SPOUSE,
                    )
                ).scalar_one_or_none()

                if not existing:
                    # Create bidirectional spouse relationship
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
                    effects.spouse_relationship_created = True

                # Generate household name
                if person.last_name == spouse.last_name:
                    household_name = f"The {person.last_name} Family"
                else:
                    household_name = f"{person.last_name} & {spouse.last_name} Family"

                # Create new household
                household = Household(
                    name=household_name,
                    origin_sacrament_id=sacrament.id,
                )
                self.db.add(household)
                self.db.flush()

                # Add both as members
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

                # Store auto-created household ID in sacrament additional_data
                # Store auto-created household ID in sacrament
                sacrament.notes = (sacrament.notes or "") + " [Auto-created household]"
                effects.household_created = True

        else:
            # Spouse not in system — mark as deferred
            effects.household_deferred = True

        return effects

    def get_by_id(self, sacrament_id: int) -> Optional[Sacrament]:
        """Get a sacrament by ID."""
        return self.db.get(Sacrament, sacrament_id)

    def get_by_id_with_person(self, sacrament_id: int) -> Optional[Sacrament]:
        """Get a sacrament by ID with person data."""
        stmt = (
            select(Sacrament)
            .options(selectinload(Sacrament.person))
            .where(Sacrament.id == sacrament_id)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_person(self, person_id: int) -> list[Sacrament]:
        """Get all sacraments for a person."""
        stmt = (
            select(Sacrament)
            .where(Sacrament.person_id == person_id)
            .order_by(Sacrament.date_received)
        )
        return list(self.db.execute(stmt).scalars().all())

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
        """
        Get paginated list of sacraments with filtering.

        Returns tuple of (items, total_count).
        """
        stmt = select(Sacrament)

        # Person filter
        if person_id is not None:
            stmt = stmt.where(Sacrament.person_id == person_id)

        # Sacrament type filter
        if sacrament_type is not None:
            stmt = stmt.where(Sacrament.sacrament_type == sacrament_type)

        # Date range filters
        if date_from is not None:
            stmt = stmt.where(Sacrament.date_received >= date_from)

        if date_to is not None:
            stmt = stmt.where(Sacrament.date_received <= date_to)

        # Sorting
        sort_column = getattr(Sacrament, sort_by, Sacrament.date_received)
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()
        stmt = stmt.order_by(sort_column)

        # Apply pagination
        items, total = paginate(self.db, stmt, page, per_page)
        return items, total

    def update(
        self, sacrament_id: int, sacrament_data: SacramentUpdate
    ) -> Optional[Sacrament]:
        """Update a sacrament (partial update supported)."""
        sacrament = self.get_by_id(sacrament_id)
        if not sacrament:
            return None

        update_data = sacrament_data.model_dump(exclude_unset=True)

        # If updating type or date, validate order
        new_type = update_data.get("sacrament_type", sacrament.sacrament_type)
        new_date = update_data.get("date_received", sacrament.date_received)

        if "sacrament_type" in update_data or "date_received" in update_data:
            self._validate_sacrament_order(
                sacrament.person_id,
                new_type,
                new_date,
                exclude_sacrament_id=sacrament_id,
            )

        for field, value in update_data.items():
            setattr(sacrament, field, value)

        self.db.commit()
        self.db.refresh(sacrament)
        return sacrament

    def delete(self, sacrament_id: int) -> bool:
        """Delete a sacrament."""
        sacrament = self.get_by_id(sacrament_id)
        if not sacrament:
            return False

        self.db.delete(sacrament)
        self.db.commit()
        return True

    def get_statistics(self) -> dict[str, Any]:
        """
        Get sacrament statistics for dashboard.

        Returns counts by type and by year.
        """
        # Get counts by type
        type_counts = {}
        for sacrament_type in SacramentType:
            count_stmt = select(func.count()).where(
                Sacrament.sacrament_type == sacrament_type
            )
            count = self.db.execute(count_stmt).scalar() or 0
            type_counts[f"total_{sacrament_type.value}s"] = count

        # Get counts by year (last 5 years)
        by_year: dict[str, dict[str, int]] = {}
        current_year = date.today().year

        for year in range(current_year, current_year - 5, -1):
            year_counts: dict[str, int] = {}
            for sacrament_type in SacramentType:
                count_stmt = (
                    select(func.count())
                    .where(Sacrament.sacrament_type == sacrament_type)
                    .where(extract("year", Sacrament.date_received) == year)
                )
                count = self.db.execute(count_stmt).scalar() or 0
                year_counts[f"{sacrament_type.value}s"] = count
            by_year[str(year)] = year_counts

        return {
            **type_counts,
            "by_year": by_year,
        }
