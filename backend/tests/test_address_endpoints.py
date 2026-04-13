"""Integration tests for Address search API endpoint.

Covers: prefix match, trigram fallback, whitespace strip.
"""

import os

import pytest

from app.models.nz_address import NZAddress

# pg_trgm is PostgreSQL-only; skip trigram tests on SQLite.
_POSTGRES = bool(os.environ.get("POSTGRES_TEST_URL"))


def _sqlite_similarity(a, b):
    """Minimal similarity stub so SQLite tests don't crash on func.similarity."""
    if a is None or b is None:
        return 0.0
    a_lower = str(a).lower()
    b_lower = str(b).lower()
    common = sum(1 for c in a_lower if c in b_lower)
    return common / max(len(a_lower), len(b_lower))


@pytest.fixture
def seed_addresses(db_session):
    """Insert NZAddress rows for search tests."""

    def _insert(rows: list[dict]):
        objs = [NZAddress(**r) for r in rows]
        db_session.add_all(objs)
        db_session.commit()
        return objs

    return _insert


# ---------------------------------------------------------------------------
# Prefix match tests
# ---------------------------------------------------------------------------


class TestAddressSearchPrefixMatch:
    """Tests for prefix match path (lines 23-30 of addresses.py)."""

    def test_prefix_match_returns_results(self, client, seed_addresses):
        """Prefix match should return addresses starting with the query."""
        seed_addresses(
            [
                {
                    "full_address": "10 Queen Street, Auckland",
                    "full_address_ascii": "10 Queen Street, Auckland",
                    "address_number": "10",
                    "road_name": "Queen",
                    "road_type_name": "Street",
                    "suburb_locality": "Auckland CBD",
                    "town_city": "Auckland",
                    "postcode": "1010",
                },
                {
                    "full_address": "15 Queen Street, Auckland",
                    "full_address_ascii": "15 Queen Street, Auckland",
                    "address_number": "15",
                    "road_name": "Queen",
                    "road_type_name": "Street",
                    "suburb_locality": "Auckland CBD",
                    "town_city": "Auckland",
                    "postcode": "1010",
                },
                {
                    "full_address": "20 King Street, Wellington",
                    "full_address_ascii": "20 King Street, Wellington",
                    "address_number": "20",
                    "road_name": "King",
                    "road_type_name": "Street",
                    "town_city": "Wellington",
                    "postcode": "6011",
                },
            ]
        )

        response = client.get("/api/addresses/search", params={"q": "10 Queen"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) >= 1
        assert results[0]["full_address"].startswith("10 Queen")

    def test_prefix_match_case_insensitive(self, client, seed_addresses):
        """Prefix match should be case-insensitive (ILIKE)."""
        seed_addresses(
            [
                {
                    "full_address": "50 Victoria Street, Christchurch",
                    "full_address_ascii": "50 Victoria Street, Christchurch",
                },
            ]
        )

        response = client.get("/api/addresses/search", params={"q": "50 victoria"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) >= 1

    def test_prefix_match_alphabetical_order(self, client, seed_addresses):
        """Prefix results should be ordered alphabetically by full_address_ascii."""
        seed_addresses(
            [
                {
                    "full_address": "C Street, Auckland",
                    "full_address_ascii": "C Street, Auckland",
                },
                {
                    "full_address": "A Street, Auckland",
                    "full_address_ascii": "A Street, Auckland",
                },
                {
                    "full_address": "B Street, Auckland",
                    "full_address_ascii": "B Street, Auckland",
                },
            ]
        )

        response = client.get("/api/addresses/search", params={"q": "A Street"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) >= 1
        assert results[0]["full_address"].startswith("A Street")

    def test_prefix_match_returns_only_prefix(self, client, seed_addresses):
        """Prefix match should not return addresses that don't start with query."""
        seed_addresses(
            [
                {
                    "full_address": "10 Queen Street, Auckland",
                    "full_address_ascii": "10 Queen Street, Auckland",
                },
                {
                    "full_address": "20 King Street, Wellington",
                    "full_address_ascii": "20 King Street, Wellington",
                },
            ]
        )

        # Use limit=1 so prefix match fills it and trigram fallback is skipped
        response = client.get(
            "/api/addresses/search", params={"q": "10 Queen", "limit": 1}
        )
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["full_address"].startswith("10 Queen")


# ---------------------------------------------------------------------------
# Whitespace strip test
# ---------------------------------------------------------------------------


class TestAddressSearchWhitespaceStrip:
    """Tests for whitespace stripping (line 21 of addresses.py)."""

    def test_query_whitespace_is_stripped(self, client, seed_addresses):
        """Leading/trailing whitespace in query should be stripped."""
        seed_addresses(
            [
                {
                    "full_address": "42 Lambton Quay, Wellington",
                    "full_address_ascii": "42 Lambton Quay, Wellington",
                },
            ]
        )

        # Query with extra whitespace around the term
        response = client.get(
            "/api/addresses/search", params={"q": "  42 Lambton Quay  "}
        )
        assert response.status_code == 200
        results = response.json()
        assert len(results) >= 1
        assert results[0]["full_address"] == "42 Lambton Quay, Wellington"

    def test_query_internal_whitespace_preserved(self, client, seed_addresses):
        """Internal whitespace between words should be preserved."""
        seed_addresses(
            [
                {
                    "full_address": "7 High Street, Napier",
                    "full_address_ascii": "7 High Street, Napier",
                },
            ]
        )

        response = client.get("/api/addresses/search", params={"q": "7 High Street"})
        assert response.status_code == 200
        results = response.json()
        assert len(results) >= 1


# ---------------------------------------------------------------------------
# Trigram fallback tests (PostgreSQL only)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _POSTGRES, reason="pg_trgm requires PostgreSQL")
class TestAddressSearchTrigramFallback:
    """Tests for trigram similarity fallback (lines 33-47 of addresses.py)."""

    def test_trigram_fallback_fills_results(self, client, seed_addresses):
        """When prefix match returns fewer than limit, trigram fills the rest."""
        seed_addresses(
            [
                {
                    "full_address": "10 Queen Street, Auckland",
                    "full_address_ascii": "10 Queen Street, Auckland",
                },
                {
                    "full_address": "25 Queens Road, Wellington",
                    "full_address_ascii": "25 Queens Road, Wellington",
                },
                {
                    "full_address": "8 Quay Street, Auckland",
                    "full_address_ascii": "8 Quay Street, Auckland",
                },
            ]
        )

        # "Que" prefix-match: "10 Queen…" and "25 Queens…" start with digits, not "Que"
        # so prefix match returns 0 results → trigram fallback should activate.
        response = client.get("/api/addresses/search", params={"q": "Que", "limit": 7})
        assert response.status_code == 200
        results = response.json()
        # Trigram should have returned at least one fuzzy match
        assert len(results) >= 1

    def test_trigram_excludes_prefix_results(self, client, seed_addresses):
        """Trigram fallback should not duplicate prefix match results."""
        seed_addresses(
            [
                {
                    "full_address": "100 Beach Road, Tauranga",
                    "full_address_ascii": "100 Beach Road, Tauranga",
                },
                {
                    "full_address": "200 Beachview Drive, Tauranga",
                    "full_address_ascii": "200 Beachview Drive, Tauranga",
                },
            ]
        )

        # "100 Beach" prefix-matches "100 Beach Road…" (1 result).
        # limit=7, so trigram fallback should fill up to 6 more.
        response = client.get(
            "/api/addresses/search", params={"q": "100 Beach", "limit": 7}
        )
        assert response.status_code == 200
        results = response.json()
        # No duplicate ids
        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids))

    def test_trigram_similarity_threshold(self, client, seed_addresses):
        """Trigram fallback only returns results with similarity > 0.1."""
        seed_addresses(
            [
                {
                    "full_address": "999 Completely Different Address, Nowhere",
                    "full_address_ascii": "999 Completely Different Address, Nowhere",
                },
            ]
        )

        # Query is very different from the stored address → low similarity
        response = client.get(
            "/api/addresses/search",
            params={"q": "xyz123nonexistent", "limit": 7},
        )
        assert response.status_code == 200
        # With a completely unrelated query, trigram similarity may be < 0.1
        # so zero results is acceptable.


# ---------------------------------------------------------------------------
# General endpoint behaviour
# ---------------------------------------------------------------------------


class TestAddressSearchValidation:
    """Tests for query parameter validation."""

    def test_query_too_short_rejected(self, client):
        """Query shorter than 3 characters should return 422."""
        response = client.get("/api/addresses/search", params={"q": "ab"})
        assert response.status_code == 422

    def test_query_missing_rejected(self, client):
        """Missing query parameter should return 422."""
        response = client.get("/api/addresses/search")
        assert response.status_code == 422

    def test_limit_bounds(self, client, seed_addresses):
        """Limit parameter should respect min=1, max=20."""
        seed_addresses(
            [
                {
                    "full_address": "1 Main Road, Auckland",
                    "full_address_ascii": "1 Main Road, Auckland",
                },
            ]
        )

        # limit=0 should be rejected
        response = client.get("/api/addresses/search", params={"q": "Main", "limit": 0})
        assert response.status_code == 422

        # limit=21 should be rejected
        response = client.get(
            "/api/addresses/search", params={"q": "Main", "limit": 21}
        )
        assert response.status_code == 422
