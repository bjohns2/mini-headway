from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.patient.repositories import patient_repository
from app.modules.patient.schemas.patient import PatientRead
from app.modules.patient.schemas.readiness import PatientReadinessResponse
from app.modules.patient.services import patient_readiness_service

router = APIRouter(tags=["patient"])


@router.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)) -> PatientRead:
    patient = patient_repository.get(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientRead.model_validate(patient)


@router.get("/patients/{patient_id}/readiness", response_model=PatientReadinessResponse)
def get_patient_readiness(
    patient_id: int, db: Session = Depends(get_db)
) -> PatientReadinessResponse:
    if patient_repository.get(db, patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient_readiness_service.compute_readiness(db, patient_id)
