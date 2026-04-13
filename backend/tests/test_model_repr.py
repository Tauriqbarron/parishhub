"""Tests for model __repr__ methods."""

from datetime import date


from app.models.analytics import (
    Birth,
    MassAttendance,
    ParishStatistic,
    MetricType,
    PopulationSnapshot,
)
from app.models.death import Death
from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.person import Person
from app.models.relationship import FamilyRelationship, RelationshipType
from app.models.sacrament import Sacrament, SacramentType
from app.models.settings import Setting


def test_person_repr(db_session):
    p = Person(first_name="John", last_name="Smith")
    db_session.add(p)
    db_session.flush()
    r = repr(p)
    assert "Person" in r
    assert "John" in r
    assert "Smith" in r
    assert str(p.id) in r


def test_household_repr(db_session):
    h = Household(name="The Smiths")
    db_session.add(h)
    db_session.flush()
    r = repr(h)
    assert "Household" in r
    assert "The Smiths" in r
    assert str(h.id) in r


def test_household_member_repr(db_session):
    h = Household(name="House A")
    p = Person(first_name="Jane", last_name="Doe")
    db_session.add_all([h, p])
    db_session.flush()
    m = HouseholdMember(household_id=h.id, person_id=p.id, role=HouseholdRole.HEAD)
    db_session.add(m)
    db_session.flush()
    r = repr(m)
    assert "HouseholdMember" in r
    assert str(h.id) in r
    assert str(p.id) in r
    assert "head" in r


def test_family_relationship_repr(db_session):
    p1 = Person(first_name="Parent", last_name="A")
    p2 = Person(first_name="Child", last_name="A")
    db_session.add_all([p1, p2])
    db_session.flush()
    rel = FamilyRelationship(
        person_id=p1.id,
        related_person_id=p2.id,
        relationship_type=RelationshipType.PARENT,
    )
    db_session.add(rel)
    db_session.flush()
    r = repr(rel)
    assert "FamilyRelationship" in r
    assert str(p1.id) in r
    assert str(p2.id) in r
    assert "parent" in r


def test_death_repr(db_session):
    p = Person(first_name="Late", last_name="Person")
    db_session.add(p)
    db_session.flush()
    d = Death(person_id=p.id, date_of_death=date(2024, 1, 1))
    db_session.add(d)
    db_session.flush()
    r = repr(d)
    assert "Death" in r
    assert str(p.id) in r
    assert "2024-01-01" in r
    assert str(d.id) in r


def test_sacrament_repr(db_session):
    p = Person(first_name="Felix", last_name="Garcia")
    db_session.add(p)
    db_session.flush()
    s = Sacrament(
        person_id=p.id,
        sacrament_type=SacramentType.BAPTISM,
        date_received=date(2020, 6, 15),
    )
    db_session.add(s)
    db_session.flush()
    r = repr(s)
    assert "Sacrament" in r
    assert str(p.id) in r
    assert "baptism" in r
    assert str(s.id) in r


def test_parish_statistic_repr(db_session):
    stat = ParishStatistic(
        metric_type=MetricType.BIRTH,
        date=date(2024, 1, 1),
        value=42,
    )
    db_session.add(stat)
    db_session.flush()
    r = repr(stat)
    assert "ParishStatistic" in r
    assert str(stat.id) in r
    assert "BIRTH" in r
    assert "2024-01-01" in r


def test_birth_repr(db_session):
    b = Birth(
        baby_first_name="Baby",
        baby_last_name="Doe",
        date_of_birth=date(2024, 3, 10),
    )
    db_session.add(b)
    db_session.flush()
    r = repr(b)
    assert "Birth" in r
    assert "Baby" in r
    assert "Doe" in r
    assert str(b.id) in r


def test_mass_attendance_repr(db_session):
    ma = MassAttendance(
        date=date(2024, 5, 1),
        attendance_count=150,
    )
    db_session.add(ma)
    db_session.flush()
    r = repr(ma)
    assert "MassAttendance" in r
    assert str(ma.id) in r
    assert "2024-05-01" in r
    assert "150" in r


def test_mass_attendance_mass_time_name_with_relation(db_session):
    """Test mass_time_name property when mass_time_rel is set."""
    from app.models.mass_times import MassTime
    from datetime import time as time_type

    mt = MassTime(name="Sunday 9am", time=time_type(9, 0))
    db_session.add(mt)
    db_session.flush()

    ma = MassAttendance(
        date=date(2024, 5, 1),
        attendance_count=100,
        mass_time_id=mt.id,
    )
    db_session.add(ma)
    db_session.flush()
    db_session.refresh(ma)

    assert ma.mass_time_name == "Sunday 9am"
    assert ma.mass_time_time == "09:00"


def test_mass_attendance_mass_time_name_without_relation(db_session):
    """Test mass_time_name property when mass_time_rel is None."""
    ma = MassAttendance(
        date=date(2024, 5, 1),
        attendance_count=50,
        mass_time="Fallback name",
    )
    db_session.add(ma)
    db_session.flush()
    db_session.refresh(ma)

    assert ma.mass_time_name == "Fallback name"
    assert ma.mass_time_time is None


def test_population_snapshot_repr(db_session):
    ps = PopulationSnapshot(
        date=date(2024, 1, 1),
        registered_members=500,
        households=120,
    )
    db_session.add(ps)
    db_session.flush()
    r = repr(ps)
    assert "PopulationSnapshot" in r
    assert str(ps.id) in r
    assert "2024-01-01" in r
    assert "500" in r


def test_setting_repr(db_session):
    s = Setting(key="parish_name", value="St. Mary's")
    db_session.add(s)
    db_session.flush()
    r = repr(s)
    assert "Setting" in r
    assert "parish_name" in r
