"""
Seed data for mini-headway.

Run via `make seed` or directly: `python -m app.seed --reset`.

Most patients have a normal, consistent eligibility state. One patient has a
state that mirrors a desync we've seen in production data, where a denormalized
field on user_insurance and the latest eligibility lookup disagree. This is
intentional — investigating it is part of the interview exercise.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.modules.insurance.models.eligibility_lookup import EligibilityLookup
from app.modules.insurance.models.user_insurance import (
    EligibilityStatus,
    UserInsurance,
)
from app.modules.patient.models.patient import Patient
from app.modules.provider.models.provider import Provider
from app.modules.scheduling.models.appointment import Appointment, AppointmentStatus


def _is_empty(db: Session) -> bool:
    return db.execute(select(Patient).limit(1)).scalar_one_or_none() is None


def _reset() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def _seed(db: Session) -> None:
    today = date.today()

    dr_adams = Provider(
        id=1,
        name="Dr. Adams",
        license_state="NY",
        license_expires_on=today + timedelta(days=365),
    )
    dr_brooks = Provider(
        id=2,
        name="Dr. Brooks",
        license_state="CA",
        license_expires_on=today + timedelta(days=180),
    )
    db.add_all([dr_adams, dr_brooks])

    patients = [
        Patient(id=1, name="Jordan Lee", date_of_birth=date(1988, 3, 12)),
        Patient(id=2, name="Sam Rivera", date_of_birth=date(1995, 7, 24)),
        Patient(id=3, name="Maya Patel", date_of_birth=date(1991, 11, 4)),
        Patient(id=4, name="Alex Chen", date_of_birth=date(1979, 1, 19)),
        Patient(id=5, name="Riley Park", date_of_birth=date(2001, 9, 30)),
        Patient(id=6, name="Casey Morgan", date_of_birth=date(1985, 5, 8)),
    ]
    db.add_all(patients)
    db.flush()

    # Five patients with healthy, consistent eligibility state.
    healthy = [
        ("Aetna", "AET001"),
        ("BlueCross", "BCB002"),
        # (skip Maya — id=3 — handled below)
        ("Cigna", "CIG004"),
        ("UnitedHealth", "UHC005"),
        ("Humana", "HUM006"),
    ]
    healthy_patient_ids = [1, 2, 4, 5, 6]
    for (carrier, member_id), patient_id in zip(healthy, healthy_patient_ids, strict=True):
        ui = UserInsurance(
            patient_id=patient_id,
            carrier_name=carrier,
            member_id=member_id,
            eligibility_status=EligibilityStatus.VERIFIED,
        )
        db.add(ui)
        db.flush()
        db.add(
            EligibilityLookup(
                user_insurance_id=ui.id,
                ran_at=datetime.combine(today, time(8, 0)) - timedelta(days=2),
                is_claim_ready=True,
                mental_health_covered=True,
                notes="Verified via payer API.",
            )
        )

    # Maya Patel (id=3): the user_insurance row says VERIFIED — that's what got
    # written when her first eligibility lookup came back green a few weeks ago.
    # But a fresher lookup ran yesterday and came back claim-ready=False with
    # mental health no longer covered, and only the eligibility_lookups row was
    # written for that one. The denormalized status on user_insurance was never
    # updated.
    maya_ui = UserInsurance(
        patient_id=3,
        carrier_name="MeridianHealth",
        member_id="MRD003",
        eligibility_status=EligibilityStatus.VERIFIED,
    )
    db.add(maya_ui)
    db.flush()
    db.add(
        EligibilityLookup(
            user_insurance_id=maya_ui.id,
            ran_at=datetime.combine(today, time(9, 0)) - timedelta(days=21),
            is_claim_ready=True,
            mental_health_covered=True,
            notes="Initial verification.",
        )
    )
    db.add(
        EligibilityLookup(
            user_insurance_id=maya_ui.id,
            ran_at=datetime.combine(today, time(9, 0)) - timedelta(days=1),
            is_claim_ready=False,
            mental_health_covered=False,
            notes="Plan switched to non-MH-covered tier mid-year.",
        )
    )

    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    # Day-before-yesterday: a normal day of confirmed sessions for Dr. Adams.
    db.add_all(
        [
            Appointment(
                patient_id=1,
                provider_id=1,
                starts_at=datetime.combine(two_days_ago, time(9, 0)),
                status=AppointmentStatus.CONFIRMED,
            ),
            Appointment(
                patient_id=2,
                provider_id=1,
                starts_at=datetime.combine(two_days_ago, time(10, 30)),
                status=AppointmentStatus.CONFIRMED,
            ),
            Appointment(
                patient_id=4,
                provider_id=1,
                starts_at=datetime.combine(two_days_ago, time(14, 0)),
                status=AppointmentStatus.CONFIRMED,
            ),
        ]
    )

    # Yesterday: mostly confirmed, plus the first sign of trouble with Maya —
    # her appointment was scheduled but never confirmed before the day rolled
    # over. (The provider would have noticed Confirm errored.) Also one
    # cancellation, for realism.
    db.add_all(
        [
            Appointment(
                patient_id=1,
                provider_id=1,
                starts_at=datetime.combine(yesterday, time(9, 0)),
                status=AppointmentStatus.CONFIRMED,
            ),
            Appointment(
                patient_id=3,  # Maya — was scheduled, never made it to CONFIRMED
                provider_id=1,
                starts_at=datetime.combine(yesterday, time(11, 0)),
                status=AppointmentStatus.SCHEDULED,
            ),
            Appointment(
                patient_id=5,
                provider_id=1,
                starts_at=datetime.combine(yesterday, time(13, 30)),
                status=AppointmentStatus.CANCELLED,
            ),
            Appointment(
                patient_id=6,
                provider_id=1,
                starts_at=datetime.combine(yesterday, time(15, 0)),
                status=AppointmentStatus.CONFIRMED,
            ),
        ]
    )

    # Today's appointments for Dr. Adams (provider_id=1).
    db.add_all(
        [
            Appointment(
                patient_id=1,
                provider_id=1,
                starts_at=datetime.combine(today, time(9, 0)),
                status=AppointmentStatus.SCHEDULED,
            ),
            Appointment(
                patient_id=2,
                provider_id=1,
                starts_at=datetime.combine(today, time(11, 0)),
                status=AppointmentStatus.SCHEDULED,
            ),
            Appointment(
                patient_id=3,  # Maya — the bug case for the README brief
                provider_id=1,
                starts_at=datetime.combine(today, time(14, 0)),
                status=AppointmentStatus.SCHEDULED,
            ),
            Appointment(
                patient_id=4,
                provider_id=1,
                starts_at=datetime.combine(today, time(15, 30)),
                status=AppointmentStatus.SCHEDULED,
            ),
            Appointment(
                patient_id=5,
                provider_id=1,
                starts_at=datetime.combine(today, time(16, 30)),
                status=AppointmentStatus.SCHEDULED,
            ),
            Appointment(
                patient_id=6,
                provider_id=2,
                starts_at=datetime.combine(today, time(10, 0)),
                status=AppointmentStatus.SCHEDULED,
            ),
        ]
    )

    db.commit()


def seed_if_empty() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if _is_empty(db):
            _seed(db)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed the mini-headway database.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before seeding.",
    )
    args = parser.parse_args(argv)

    if args.reset:
        _reset()
    else:
        Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        if not _is_empty(db):
            print("Database already has data. Pass --reset to drop and reseed.")
            return 0
        _seed(db)
    print("Seeded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
