from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.scheduling.models.appointment import Appointment


def get(db: Session, appointment_id: int) -> Appointment | None:
    return db.get(Appointment, appointment_id)


def list_for_provider_on(
    db: Session, provider_id: int, day: date
) -> list[Appointment]:
    start = datetime.combine(day, time.min)
    end = datetime.combine(day, time.max)
    stmt = (
        select(Appointment)
        .where(Appointment.provider_id == provider_id)
        .where(Appointment.starts_at >= start)
        .where(Appointment.starts_at <= end)
        .order_by(Appointment.starts_at.asc())
    )
    return list(db.execute(stmt).scalars())
