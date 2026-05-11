from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import current_provider_id
from app.modules.patient.repositories import patient_repository
from app.modules.provider.repositories import provider_repository
from app.modules.provider.schemas.confirmability import ConfirmabilityResponse
from app.modules.provider.services import session_confirmability_service
from app.modules.scheduling.models.appointment import AppointmentStatus
from app.modules.scheduling.repositories import appointment_repository
from app.modules.scheduling.schemas.appointment import (
    AppointmentRead,
    AppointmentWithPatient,
)

router = APIRouter(tags=["scheduling"])


def _attach_names(db: Session, appointment) -> AppointmentWithPatient:
    patient = patient_repository.get(db, appointment.patient_id)
    provider = provider_repository.get(db, appointment.provider_id)
    return AppointmentWithPatient(
        id=appointment.id,
        patient_id=appointment.patient_id,
        provider_id=appointment.provider_id,
        starts_at=appointment.starts_at,
        status=appointment.status,
        patient_name=patient.name if patient else "Unknown",
        provider_name=provider.name if provider else "Unknown",
    )


@router.get("/appointments", response_model=list[AppointmentWithPatient])
def list_appointments(
    day: date_type = Query(default_factory=date_type.today),
    db: Session = Depends(get_db),
    provider_id: int = Depends(current_provider_id),
) -> list[AppointmentWithPatient]:
    appointments = appointment_repository.list_for_provider_on(db, provider_id, day)
    return [_attach_names(db, a) for a in appointments]


@router.get("/appointments/{appointment_id}", response_model=AppointmentWithPatient)
def get_appointment(
    appointment_id: int, db: Session = Depends(get_db)
) -> AppointmentWithPatient:
    appointment = appointment_repository.get(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return _attach_names(db, appointment)


@router.get(
    "/appointments/{appointment_id}/confirmability",
    response_model=ConfirmabilityResponse,
)
def get_confirmability(
    appointment_id: int, db: Session = Depends(get_db)
) -> ConfirmabilityResponse:
    appointment = appointment_repository.get(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return session_confirmability_service.get_confirmability(db, appointment)


@router.post(
    "/appointments/{appointment_id}/confirm", response_model=AppointmentRead
)
def confirm_appointment(
    appointment_id: int, db: Session = Depends(get_db)
) -> AppointmentRead:
    appointment = appointment_repository.get(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")

    confirmability = session_confirmability_service.get_confirmability(db, appointment)
    if not confirmability.is_confirmable:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Appointment is not confirmable.",
                "blockers": [b.model_dump() for b in confirmability.blockers],
            },
        )

    appointment.status = AppointmentStatus.CONFIRMED
    db.commit()
    db.refresh(appointment)
    return AppointmentRead.model_validate(appointment)
