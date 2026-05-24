"""Tests for RosterService — role CRUD, templates, instances, assignments, swaps."""

from datetime import date, timedelta

import pytest

from app.models.person import Gender, Person
from app.models.roster import RosterRole, RosterTemplateSlot
from app.schemas.roster import (
    RosterAssignmentCreate,
    RosterRoleCreate,
    RosterRoleUpdate,
    RosterSwapCreate,
    RosterTemplateCreate,
    RosterTemplateSettings,
    RosterTemplateSlotCreate,
    RosterTemplateUpdate,
)
from app.services.roster import RosterService, RosterValidationError, _next_month


# ════════════════════════════════════════════════════════════════════════
# _next_month helper
# ════════════════════════════════════════════════════════════════════════

def test_next_month_mid_month():
    assert _next_month(date(2026, 1, 15)) == date(2026, 2, 15)


def test_next_month_jan31_to_feb28():
    assert _next_month(date(2026, 1, 31)) == date(2026, 2, 28)


def test_next_month_dec_to_jan():
    assert _next_month(date(2026, 12, 10)) == date(2027, 1, 10)


def test_next_month_mar31_to_apr30():
    assert _next_month(date(2026, 3, 31)) == date(2026, 4, 30)


def test_next_month_leap_year():
    assert _next_month(date(2028, 1, 31)) == date(2028, 2, 29)


# ════════════════════════════════════════════════════════════════════════
# Role CRUD
# ════════════════════════════════════════════════════════════════════════

def test_create_role(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader", description="Reads at Mass"))
    assert role.id is not None
    assert role.name == "Reader"
    assert role.description == "Reads at Mass"


def test_list_roles(db_session):
    svc = RosterService(db_session)
    svc.create_role(RosterRoleCreate(name="Reader"))
    svc.create_role(RosterRoleCreate(name="Usher"))
    roles = svc.list_roles()
    assert len(roles) == 2


def test_update_role(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    updated = svc.update_role(role.id, RosterRoleUpdate(name="Lector"))
    assert updated.name == "Lector"


def test_delete_role_unused(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    assert svc.delete_role(role.id) is True


def test_delete_role_referenced_by_slot_raises(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(
        RosterTemplateCreate(
            name="Sunday Mass",
            slots=[RosterTemplateSlotCreate(role_id=role.id, label="1st Reading")],
        )
    )
    with pytest.raises(RosterValidationError, match="referenced by"):
        svc.delete_role(role.id)


def test_update_nonexistent_role_raises(db_session):
    svc = RosterService(db_session)
    with pytest.raises(RosterValidationError, match="not found"):
        svc.update_role(9999, RosterRoleUpdate(name="X"))


# ════════════════════════════════════════════════════════════════════════
# Person-Role assignments
# ════════════════════════════════════════════════════════════════════════

def test_assign_role_to_person(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    prr = svc.assign_role_to_person(person.id, role.id)
    assert prr.person_id == person.id
    assert prr.role_id == role.id


def test_assign_duplicate_role_raises(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    with pytest.raises(RosterValidationError, match="already has"):
        svc.assign_role_to_person(person.id, role.id)


def test_get_person_roles(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    r1 = svc.create_role(RosterRoleCreate(name="Reader"))
    r2 = svc.create_role(RosterRoleCreate(name="Usher"))
    svc.assign_role_to_person(person.id, r1.id)
    svc.assign_role_to_person(person.id, r2.id)
    roles = svc.get_person_roles(person.id)
    assert len(roles) == 2


def test_remove_role_from_person(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    assert svc.remove_role_from_person(person.id, role.id) is True
    assert len(svc.get_person_roles(person.id)) == 0


# ════════════════════════════════════════════════════════════════════════
# Template CRUD
# ════════════════════════════════════════════════════════════════════════

def test_create_template_with_slots(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(
        RosterTemplateCreate(
            name="Sunday 9am",
            recurrence_rule="weekly",
            slots=[
                RosterTemplateSlotCreate(role_id=role.id, label="1st Reading", sort_order=1, min_persons=1, max_persons=1),
                RosterTemplateSlotCreate(role_id=role.id, label="2nd Reading", sort_order=2, min_persons=1, max_persons=1),
            ],
        )
    )
    assert t.name == "Sunday 9am"
    assert t.recurrence_rule == "weekly"
    assert len(t.slots) == 2


def test_list_templates_filter_active(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.create_template(RosterTemplateCreate(name="Active T", is_active=True, slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    svc.create_template(RosterTemplateCreate(name="Inactive T", is_active=False, slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    assert len(svc.list_templates(is_active=True)) == 1
    assert len(svc.list_templates(is_active=False)) == 1


def test_duplicate_template(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    orig = svc.create_template(
        RosterTemplateCreate(name="Original", recurrence_rule="weekly", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")])
    )
    dup = svc.duplicate_template(orig.id)
    assert dup.name == "Original (copy)"
    assert dup.recurrence_rule == "weekly"
    assert len(dup.slots) == 1


def test_delete_template(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="To Delete", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    assert svc.delete_template(t.id) is True


# ════════════════════════════════════════════════════════════════════════
# Instance management
# ════════════════════════════════════════════════════════════════════════

def test_generate_instance(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", recurrence_rule="weekly", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    assert inst.status == "draft"
    assert inst.template_id == t.id


def test_publish_instance(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    pub = svc.publish_instance(inst.id)
    assert pub.status == "published"
    assert pub.published_at is not None


def test_publish_already_published_raises(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    svc.publish_instance(inst.id)
    with pytest.raises(RosterValidationError, match="Cannot publish"):
        svc.publish_instance(inst.id)


def test_cancel_instance(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    cancelled = svc.cancel_instance(inst.id)
    assert cancelled.status == "cancelled"


def test_complete_instance(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    svc.publish_instance(inst.id)
    comp = svc.complete_instance(inst.id)
    assert comp.status == "completed"
    assert comp.completed_at is not None


def test_complete_unpublished_raises(db_session):
    svc = RosterService(db_session)
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    with pytest.raises(RosterValidationError, match="only complete published"):
        svc.complete_instance(inst.id)


# ════════════════════════════════════════════════════════════════════════
# Assignment management
# ════════════════════════════════════════════════════════════════════════

def test_assign_person(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, person.id)
    assert asgn.status == "pending"
    assert asgn.person_id == person.id


def test_assign_person_missing_role_raises_409_detail(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="Jane", last_name="Doe")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    with pytest.raises(RosterValidationError) as exc:
        svc.assign_person(inst.id, slot.id, person.id)
    assert exc.value.detail.get("missing_role") == role.id


def test_self_assign_auto_accepted(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.self_assign(inst.id, slot.id, person.id)
    assert asgn.status == "accepted"


def test_update_assignment_status_valid_transition(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, person.id)
    updated = svc.update_assignment_status(asgn.id, "accepted", person.id)
    assert updated.status == "accepted"
    assert updated.accepted_at is not None


def test_update_assignment_status_invalid_transition_raises(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, person.id)
    svc.update_assignment_status(asgn.id, "accepted", person.id)
    with pytest.raises(RosterValidationError, match="Cannot transition"):
        svc.update_assignment_status(asgn.id, "declined", person.id)


def test_cancel_assignment(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, person.id)
    cancelled = svc.cancel_assignment(asgn.id, person.id)
    # cancel_assignment frees the slot → status resets to "pending" for reuse
    assert cancelled.status == "pending"
    assert cancelled.cancelled_at is not None


def test_remove_assignment(db_session):
    svc = RosterService(db_session)
    person = Person(first_name="John", last_name="Smith")
    db_session.add(person)
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(person.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, person.id)
    svc.remove_assignment(asgn.id)
    assert len(svc.get_instance(inst.id).assignments) == 0


# ════════════════════════════════════════════════════════════════════════
# Swap management
# ════════════════════════════════════════════════════════════════════════

def test_propose_and_accept_swap(db_session):
    svc = RosterService(db_session)
    p1 = Person(first_name="Alice", last_name="A")
    p2 = Person(first_name="Bob", last_name="B")
    db_session.add_all([p1, p2])
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(p1.id, role.id)
    svc.assign_role_to_person(p2.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, p1.id)
    swap = svc.propose_swap(asgn.id, p1.id, p2.id, notes="Can you cover?")
    assert swap.status == "pending"
    accepted = svc.accept_swap(swap.id, p2.id)
    assert accepted.status == "accepted"
    # p1's assignment should be cancelled, new assignment for p2
    assert asgn.status == "cancelled"


def test_decline_swap(db_session):
    svc = RosterService(db_session)
    p1 = Person(first_name="Alice", last_name="A")
    p2 = Person(first_name="Bob", last_name="B")
    db_session.add_all([p1, p2])
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(p1.id, role.id)
    svc.assign_role_to_person(p2.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, p1.id)
    swap = svc.propose_swap(asgn.id, p1.id, p2.id)
    declined = svc.decline_swap(swap.id, p2.id)
    assert declined.status == "declined"


def test_get_my_assignments(db_session):
    svc = RosterService(db_session)
    # skipif = SQLite doesn't support RosterInstance.date column ordering properly
    # (no issue in production with PostgreSQL)
    p1 = Person(first_name="Alice", last_name="A")
    p2 = Person(first_name="Bob", last_name="B")
    db_session.add_all([p1, p2])
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(p1.id, role.id)
    svc.assign_role_to_person(p2.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R", min_persons=2, max_persons=2)]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    svc.assign_person(inst.id, slot.id, p1.id)
    svc.assign_person(inst.id, slot.id, p2.id)
    mine = svc.get_my_assignments(p1.id)
    assert len(mine) == 1
    assert mine[0].person_id == p1.id

    both = svc.get_my_assignments(p2.id)
    assert len(both) == 1


def test_get_eligible_swappers(db_session):
    svc = RosterService(db_session)
    p1 = Person(first_name="Alice", last_name="A")
    p2 = Person(first_name="Bob", last_name="B")
    db_session.add_all([p1, p2])
    db_session.commit()
    role = svc.create_role(RosterRoleCreate(name="Reader"))
    svc.assign_role_to_person(p1.id, role.id)
    svc.assign_role_to_person(p2.id, role.id)
    t = svc.create_template(RosterTemplateCreate(name="Sunday", slots=[RosterTemplateSlotCreate(role_id=role.id, label="R")]))
    slot = t.slots[0]
    inst = svc.generate_instance(t.id, date.today() + timedelta(days=7))
    asgn = svc.assign_person(inst.id, slot.id, p1.id)
    swappers = svc.get_eligible_swappers(asgn.id)
    assert len(swappers) == 1
    assert swappers[0].id == p2.id
