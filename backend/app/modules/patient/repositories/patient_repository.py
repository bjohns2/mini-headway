from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.patient.models.patient import Patient


def get(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def list_all(db: Session) -> list[Patient]:
    stmt = select(Patient).order_by(Patient.name.asc())
    return list(db.execute(stmt).scalars())
