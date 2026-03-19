"""API router for NZ address autocomplete using LINZ data."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.nz_address import NZAddress
from app.schemas.address import AddressSearchResult

router = APIRouter(prefix="/api/addresses", tags=["addresses"])


@router.get("/search", response_model=list[AddressSearchResult])
async def search_addresses(
    q: str = Query(..., min_length=3, description="Address search query"),
    limit: int = Query(7, ge=1, le=20),
    db: Session = Depends(get_db),
) -> list[AddressSearchResult]:
    """Search NZ addresses with fuzzy matching via pg_trgm."""
    query = q.strip()

    # Try prefix match first (fast, exact start)
    results = (
        db.query(NZAddress)
        .filter(NZAddress.full_address_ascii.ilike(f"{query}%"))
        .order_by(NZAddress.full_address_ascii)
        .limit(limit)
        .all()
    )

    # Fall back to trigram similarity if prefix match yields too few results
    if len(results) < limit:
        existing_ids = [r.id for r in results]
        trgm_results = (
            db.query(NZAddress)
            .filter(
                NZAddress.id.notin_(existing_ids) if existing_ids else True,
                func.similarity(NZAddress.full_address_ascii, query) > 0.1,
            )
            .order_by(func.similarity(NZAddress.full_address_ascii, query).desc())
            .limit(limit - len(results))
            .all()
        )
        results.extend(trgm_results)

    return [AddressSearchResult.model_validate(r) for r in results]
