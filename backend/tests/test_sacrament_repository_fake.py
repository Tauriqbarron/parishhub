"""Tests for FakeSacramentRepository — in-memory fake of SacramentRepository."""

from datetime import date

import pytest

from app.models.sacrament import SacramentType
from app.repositories.sacrament import FakeSacramentRepository
from app.schemas.sacrament import SacramentCreate, SacramentUpdate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_create(
    *,
    person_id: int = 1,
    sacrament_type: SacramentType = SacramentType.BAPTISM,
    date_received: date = date(2023, 6, 15),
    notes: str | None = None,
) -> SacramentCreate:
    return SacramentCreate(
        person_id=person_id,
        sacrament_type=sacrament_type,
        date_received=date_received,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryInit:
    def test_starts_empty(self):
        repo = FakeSacramentRepository()
        assert repo._store == {}
        assert repo._next_id == 1
        assert repo.statistics_override is None


# ---------------------------------------------------------------------------
# create
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryCreate:
    def test_create_returns_sacrament_with_assigned_id(self):
        repo = FakeSacramentRepository()
        data = _make_create()
        result = repo.create(data)

        assert result.id == 1
        assert result.person_id == 1
        assert result.sacrament_type == SacramentType.BAPTISM
        assert result.date_received == date(2023, 6, 15)

    def test_create_increments_ids(self):
        repo = FakeSacramentRepository()
        s1 = repo.create(_make_create(person_id=1))
        s2 = repo.create(_make_create(person_id=2))

        assert s1.id == 1
        assert s2.id == 2
        assert len(repo._store) == 2

    def test_create_stores_optional_fields(self):
        repo = FakeSacramentRepository()
        data = SacramentCreate(
            person_id=10,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(2020, 1, 1),
            notes="Born again",
            godfather="John",
            godmother="Mary",
            minister="Fr. Smith",
        )
        result = repo.create(data)

        assert result.notes == "Born again"
        assert result.godfather == "John"
        assert result.godmother == "Mary"
        assert result.minister == "Fr. Smith"


# ---------------------------------------------------------------------------
# get_by_id / get_by_id_with_person
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryGetById:
    def test_returns_existing(self):
        repo = FakeSacramentRepository()
        created = repo.create(_make_create())

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_returns_none_for_missing(self):
        repo = FakeSacramentRepository()
        assert repo.get_by_id(999) is None

    def test_get_by_id_with_person_returns_same(self):
        repo = FakeSacramentRepository()
        created = repo.create(_make_create())

        result = repo.get_by_id_with_person(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_with_person_returns_none_for_missing(self):
        repo = FakeSacramentRepository()
        assert repo.get_by_id_with_person(999) is None


# ---------------------------------------------------------------------------
# get_by_person
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryGetByPerson:
    def test_returns_sacraments_for_person(self):
        repo = FakeSacramentRepository()
        repo.create(_make_create(person_id=5, date_received=date(2023, 1, 1)))
        repo.create(_make_create(person_id=5, date_received=date(2024, 1, 1)))
        repo.create(_make_create(person_id=7, date_received=date(2023, 6, 1)))

        results = repo.get_by_person(5)
        assert len(results) == 2
        assert all(s.person_id == 5 for s in results)

    def test_returns_empty_for_unknown_person(self):
        repo = FakeSacramentRepository()
        assert repo.get_by_person(999) == []


# ---------------------------------------------------------------------------
# get_sacraments_by_person
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryGetSacramentsByPerson:
    def test_returns_dict_keyed_by_type(self):
        repo = FakeSacramentRepository()
        repo.create(
            _make_create(
                person_id=1,
                sacrament_type=SacramentType.BAPTISM,
                date_received=date(2020, 1, 1),
            )
        )
        repo.create(
            _make_create(
                person_id=1,
                sacrament_type=SacramentType.CONFIRMATION,
                date_received=date(2023, 6, 1),
            )
        )

        result = repo.get_sacraments_by_person(1)
        assert SacramentType.BAPTISM in result
        assert SacramentType.CONFIRMATION in result
        assert result[SacramentType.BAPTISM].sacrament_type == SacramentType.BAPTISM

    def test_empty_for_unknown_person(self):
        repo = FakeSacramentRepository()
        assert repo.get_sacraments_by_person(999) == {}


# ---------------------------------------------------------------------------
# get_list — pagination, filters, sort
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryGetList:
    @pytest.fixture()
    def populated_repo(self) -> FakeSacramentRepository:
        repo = FakeSacramentRepository()
        records = [
            (1, SacramentType.BAPTISM, date(2020, 3, 15)),
            (1, SacramentType.FIRST_COMMUNION, date(2021, 5, 10)),
            (1, SacramentType.CONFIRMATION, date(2023, 6, 1)),
            (2, SacramentType.BAPTISM, date(2019, 1, 20)),
            (2, SacramentType.MARRIAGE, date(2022, 9, 1)),
        ]
        for pid, stype, d in records:
            repo.create(
                _make_create(person_id=pid, sacrament_type=stype, date_received=d)
            )
        return repo

    def test_returns_all_when_no_filters(self, populated_repo):
        items, total = populated_repo.get_list()
        assert total == 5
        assert len(items) == 5

    def test_pagination(self, populated_repo):
        items, total = populated_repo.get_list(page=1, per_page=2)
        assert total == 5
        assert len(items) == 2

        items2, total2 = populated_repo.get_list(page=3, per_page=2)
        assert total2 == 5
        assert len(items2) == 1  # last page

    def test_filter_by_person_id(self, populated_repo):
        items, total = populated_repo.get_list(person_id=1)
        assert total == 3
        assert all(s.person_id == 1 for s in items)

    def test_filter_by_sacrament_type(self, populated_repo):
        items, total = populated_repo.get_list(sacrament_type=SacramentType.BAPTISM)
        assert total == 2
        assert all(s.sacrament_type == SacramentType.BAPTISM for s in items)

    def test_filter_by_date_from(self, populated_repo):
        items, total = populated_repo.get_list(date_from=date(2021, 1, 1))
        assert total == 3
        assert all(s.date_received >= date(2021, 1, 1) for s in items)

    def test_filter_by_date_to(self, populated_repo):
        items, total = populated_repo.get_list(date_to=date(2020, 12, 31))
        assert total == 2
        assert all(s.date_received <= date(2020, 12, 31) for s in items)

    def test_filter_by_date_range(self, populated_repo):
        items, total = populated_repo.get_list(
            date_from=date(2020, 1, 1), date_to=date(2021, 12, 31)
        )
        assert total == 2
        assert all(
            date(2020, 1, 1) <= s.date_received <= date(2021, 12, 31) for s in items
        )

    def test_combined_filters(self, populated_repo):
        items, total = populated_repo.get_list(
            person_id=1, sacrament_type=SacramentType.BAPTISM
        )
        assert total == 1
        assert items[0].person_id == 1
        assert items[0].sacrament_type == SacramentType.BAPTISM

    def test_sort_descending(self, populated_repo):
        items, _ = populated_repo.get_list(sort_by="date_received", sort_order="desc")
        dates = [s.date_received for s in items]
        assert dates == sorted(dates, reverse=True)

    def test_sort_ascending(self, populated_repo):
        items, _ = populated_repo.get_list(sort_by="date_received", sort_order="asc")
        dates = [s.date_received for s in items]
        assert dates == sorted(dates)

    def test_sort_by_sacrament_type(self, populated_repo):
        items, _ = populated_repo.get_list(sort_by="sacrament_type", sort_order="asc")
        types = [s.sacrament_type.value for s in items]
        assert types == sorted(types)

    def test_empty_repo(self):
        repo = FakeSacramentRepository()
        items, total = repo.get_list()
        assert total == 0
        assert items == []


# ---------------------------------------------------------------------------
# update
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryUpdate:
    def test_update_existing(self):
        repo = FakeSacramentRepository()
        created = repo.create(_make_create(notes="old"))

        updated = repo.update(
            created.id,
            SacramentUpdate(notes="new", minister="Fr. Jones"),
        )

        assert updated is not None
        assert updated.notes == "new"
        assert updated.minister == "Fr. Jones"
        # Unchanged fields preserved
        assert updated.person_id == created.person_id

    def test_update_nonexistent_returns_none(self):
        repo = FakeSacramentRepository()
        assert repo.update(999, SacramentUpdate(notes="x")) is None

    def test_update_only_specified_fields(self):
        repo = FakeSacramentRepository()
        data = SacramentCreate(
            person_id=1,
            sacrament_type=SacramentType.BAPTISM,
            date_received=date(2023, 6, 15),
            notes="keep",
            godfather="keep_gf",
        )
        created = repo.create(data)

        updated = repo.update(created.id, SacramentUpdate(notes="changed"))

        assert updated is not None
        assert updated.notes == "changed"
        assert updated.godfather == "keep_gf"  # not overwritten


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryDelete:
    def test_delete_existing(self):
        repo = FakeSacramentRepository()
        created = repo.create(_make_create())

        assert repo.delete(created.id) is True
        assert repo.get_by_id(created.id) is None
        assert len(repo._store) == 0

    def test_delete_nonexistent(self):
        repo = FakeSacramentRepository()
        assert repo.delete(999) is False

    def test_delete_only_removes_target(self):
        repo = FakeSacramentRepository()
        s1 = repo.create(_make_create(person_id=1))
        s2 = repo.create(_make_create(person_id=2))

        repo.delete(s1.id)
        assert repo.get_by_id(s1.id) is None
        assert repo.get_by_id(s2.id) is not None


# ---------------------------------------------------------------------------
# get_statistics
# ---------------------------------------------------------------------------


class TestFakeSacramentRepositoryGetStatistics:
    def test_empty_statistics(self):
        repo = FakeSacramentRepository()
        stats = repo.get_statistics()

        # All types should be 0
        for stype in SacramentType:
            assert stats[f"total_{stype.value}s"] == 0

        # by_year key should exist with last 5 years
        assert "by_year" in stats
        current_year = date.today().year
        expected_years = {str(y) for y in range(current_year, current_year - 5, -1)}
        assert set(stats["by_year"].keys()) == expected_years

    def test_counts_by_type(self):
        repo = FakeSacramentRepository()
        repo.create(_make_create(sacrament_type=SacramentType.BAPTISM))
        repo.create(_make_create(sacrament_type=SacramentType.BAPTISM))
        repo.create(_make_create(sacrament_type=SacramentType.CONFIRMATION))

        stats = repo.get_statistics()
        assert stats["total_baptisms"] == 2
        assert stats["total_confirmations"] == 1
        assert stats["total_marriages"] == 0

    def test_counts_by_year(self):
        repo = FakeSacramentRepository()
        current_year = date.today().year
        repo.create(
            _make_create(
                sacrament_type=SacramentType.BAPTISM,
                date_received=date(current_year, 3, 1),
            )
        )
        repo.create(
            _make_create(
                sacrament_type=SacramentType.BAPTISM,
                date_received=date(current_year - 1, 7, 1),
            )
        )
        # Outside the 5-year window
        repo.create(
            _make_create(
                sacrament_type=SacramentType.BAPTISM,
                date_received=date(current_year - 10, 1, 1),
            )
        )

        stats = repo.get_statistics()
        by_year = stats["by_year"]
        assert by_year[str(current_year)]["baptisms"] == 1
        assert by_year[str(current_year - 1)]["baptisms"] == 1
        # Old record should not appear in any of the last 5 years
        total_in_window = sum(
            by_year[str(y)].get("baptisms", 0)
            for y in range(current_year, current_year - 5, -1)
        )
        assert total_in_window == 2

    def test_statistics_override(self):
        repo = FakeSacramentRepository()
        override = {"total_baptisms": 42, "by_year": {}}
        repo.statistics_override = override

        assert repo.get_statistics() == override
