import enum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class EligibilityStatus(str, enum.Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    TERMINATED = "TERMINATED"


class UserInsurance(Base):
    __tablename__ = "user_insurances"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), index=True)
    carrier_name: Mapped[str] = mapped_column(String(120))
    member_id: Mapped[str] = mapped_column(String(60))
    eligibility_status: Mapped[EligibilityStatus] = mapped_column(
        Enum(EligibilityStatus), default=EligibilityStatus.UNVERIFIED
    )

    lookups: Mapped[list["EligibilityLookup"]] = relationship(  # type: ignore[name-defined]
        back_populates="user_insurance",
        order_by="EligibilityLookup.ran_at.desc()",
        cascade="all, delete-orphan",
    )
