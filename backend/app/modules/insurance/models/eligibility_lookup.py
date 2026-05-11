from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class EligibilityLookup(Base):
    __tablename__ = "eligibility_lookups"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_insurance_id: Mapped[int] = mapped_column(
        ForeignKey("user_insurances.id"), index=True
    )
    ran_at: Mapped[datetime] = mapped_column(DateTime)
    is_claim_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    mental_health_covered: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(default="")

    user_insurance: Mapped["UserInsurance"] = relationship(back_populates="lookups")


from app.modules.insurance.models.user_insurance import UserInsurance  # noqa: E402,F401
