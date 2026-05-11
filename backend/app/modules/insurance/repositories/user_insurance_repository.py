from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.insurance.models.user_insurance import UserInsurance


def get_active_for_patient(db: Session, patient_id: int) -> UserInsurance | None:
    """Returns the patient's primary insurance row, or None if they have none."""
    stmt = (
        select(UserInsurance)
        .where(UserInsurance.patient_id == patient_id)
        .order_by(UserInsurance.id.asc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()
