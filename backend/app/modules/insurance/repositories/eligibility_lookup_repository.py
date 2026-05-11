from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.insurance.models.eligibility_lookup import EligibilityLookup
from app.modules.insurance.models.user_insurance import UserInsurance


def latest_for_user_insurance(
    db: Session, user_insurance_id: int
) -> EligibilityLookup | None:
    """Most recent eligibility lookup for a UserInsurance row."""
    stmt = (
        select(EligibilityLookup)
        .where(EligibilityLookup.user_insurance_id == user_insurance_id)
        .order_by(EligibilityLookup.ran_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()


def latest_for_patient(db: Session, patient_id: int) -> EligibilityLookup | None:
    """Most recent eligibility lookup across all of this patient's insurance rows."""
    stmt = (
        select(EligibilityLookup)
        .join(UserInsurance, UserInsurance.id == EligibilityLookup.user_insurance_id)
        .where(UserInsurance.patient_id == patient_id)
        .order_by(EligibilityLookup.ran_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()
