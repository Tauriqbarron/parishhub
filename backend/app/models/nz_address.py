from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NZAddress(Base):
    """LINZ NZ Address dataset for address autocomplete."""

    __tablename__ = "nz_addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_address: Mapped[str] = mapped_column(String(400), nullable=False)
    full_address_ascii: Mapped[Optional[str]] = mapped_column(String(250))
    address_number: Mapped[Optional[str]] = mapped_column(String(20))
    road_name: Mapped[Optional[str]] = mapped_column(String(100))
    road_type_name: Mapped[Optional[str]] = mapped_column(String(50))
    suburb_locality: Mapped[Optional[str]] = mapped_column(String(100))
    town_city: Mapped[Optional[str]] = mapped_column(String(100))
    postcode: Mapped[Optional[str]] = mapped_column(String(10))
