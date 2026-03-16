"""Model for household consent records."""

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class HouseholdConsent(Base):
    """Consent record linked to a household registration."""

    __tablename__ = "household_consents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), nullable=False
    )
    data_privacy_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    photo_media_release: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    comm_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comm_sms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    comm_phone: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    terms_acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False)
    consented_at: Mapped[str] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    household = relationship("Household", backref="consents")
