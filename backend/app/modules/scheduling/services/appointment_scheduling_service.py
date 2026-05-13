from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.modules.patient.repositories import patient_repository
from app.modules.patient.services import patient_readiness_service
from app.modules.scheduling.models.appointment import Appointment, AppointmentStatus


def schedule_appointment(
    db: Session,
    *,
    provider_id: int,
    patient_id: int,
    starts_at: datetime,
) -> Appointment:
    """
    Create a new appointment, gated on the patient's readiness.

    Readiness drives the schedule gate because it's the patient-scoped, day-view
    summary — if a patient's day-view badge says "Ready", a provider should be
    able to book them. (Separately, each individual session still has to clear
    `session_confirmability_service` before it can be confirmed.)
    """
    if patient_repository.get(db, patient_id) is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    readiness = patient_readiness_service.compute_readiness(db, patient_id)
    if not readiness.is_ready:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Patient is not ready to be scheduled.",
                "issues": [i.model_dump() for i in readiness.issues],
            },
        )

    appointment = Appointment(
        patient_id=patient_id,
        provider_id=provider_id,
        starts_at=starts_at,
        status=AppointmentStatus.SCHEDULED,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
