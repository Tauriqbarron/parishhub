from typing import Optional

from pydantic import BaseModel, ConfigDict


class AddressSearchResult(BaseModel):
    """Single address result from LINZ autocomplete search."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_address: str
    address_number: Optional[str] = None
    road_name: Optional[str] = None
    road_type_name: Optional[str] = None
    suburb_locality: Optional[str] = None
    town_city: Optional[str] = None
    postcode: Optional[str] = None
