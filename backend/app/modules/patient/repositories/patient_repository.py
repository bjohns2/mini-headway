from sqlalchemy.orm import Session

from app.modules.patient.models.patient import Patient


def get(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)
