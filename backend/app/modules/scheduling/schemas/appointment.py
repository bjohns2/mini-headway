from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.scheduling.models.appointment import AppointmentStatus


class AppointmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    provider_id: int
    starts_at: datetime
    status: AppointmentStatus


class AppointmentWithPatient(AppointmentRead):
    patient_name: str
    provider_name: str


class AppointmentCreate(BaseModel):
    patient_id: int
    starts_at: datetime
