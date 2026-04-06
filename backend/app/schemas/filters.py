"""Filter dataclasses for service layer queries."""

from dataclasses import dataclass
from typing import Optional

from app.models.person import Gender
from app.models.sacrament import SacramentType


@dataclass(frozen=True)
class PersonFilter:
    """Filter parameters for PersonService.get_list()."""

    search: Optional[str] = None
    gender: Optional[Gender] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    has_sacrament: Optional[SacramentType] = None
    missing_sacrament: Optional[SacramentType] = None
    is_deceased: Optional[bool] = None
    has_household: Optional[bool] = None
