from datetime import date, datetime, timedelta

from app.modules.insurance.models.eligibility_lookup import EligibilityLookup
from app.modules.insurance.models.user_insurance import (
    EligibilityStatus,
    UserInsurance,
)
from app.modules.patient.models.patient import Patient
from app.modules.patient.services import patient_readiness_service
from app.modules.provider.models.provider import Provider
from app.modules.provider.services import session_confirmability_service
from app.modules.scheduling.models.appointment import Appointment


def _make_provider(db) -> Provider:
    provider = Provider(
        name="Dr. Test",
        license_state="NY",
        license_expires_on=date.today() + timedelta(days=365),
    )
    db.add(provider)
    db.flush()
    return provider


def _make_patient(db, name: str = "Patient One") -> Patient:
    patient = Patient(name=name, date_of_birth=date(1990, 1, 1))
    db.add(patient)
    db.flush()
    return patient


def test_healthy_patient_is_ready_and_confirmable(db):
    provider = _make_provider(db)
    patient = _make_patient(db)
    insurance = UserInsurance(
        patient_id=patient.id,
        carrier_name="Aetna",
        member_id="A1",
        eligibility_status=EligibilityStatus.VERIFIED,
    )
    db.add(insurance)
    db.flush()
    db.add(
        EligibilityLookup(
            user_insurance_id=insurance.id,
            ran_at=datetime.utcnow(),
            is_claim_ready=True,
            mental_health_covered=True,
        )
    )
    appointment = Appointment(
        patient_id=patient.id,
        provider_id=provider.id,
        starts_at=datetime.utcnow(),
    )
    db.add(appointment)
    db.flush()

    readiness = patient_readiness_service.compute_readiness(db, patient.id)
    assert readiness.is_ready
    assert readiness.issues == []

    confirmability = session_confirmability_service.get_confirmability(db, appointment)
    assert confirmability.is_confirmable
    assert confirmability.blockers == []


def test_patient_with_no_insurance_is_not_ready(db):
    patient = _make_patient(db, "No Insurance")
    readiness = patient_readiness_service.compute_readiness(db, patient.id)
    assert readiness.is_ready is False
    assert {i.type.value for i in readiness.issues} == {"MISSING_INSURANCE"}


def test_expired_provider_license_blocks_confirmation(db):
    provider = Provider(
        name="Dr. Expired",
        license_state="NY",
        license_expires_on=date.today() - timedelta(days=1),
    )
    db.add(provider)
    patient = _make_patient(db, "Has Insurance")
    insurance = UserInsurance(
        patient_id=patient.id,
        carrier_name="Aetna",
        member_id="A1",
        eligibility_status=EligibilityStatus.VERIFIED,
    )
    db.add(insurance)
    db.flush()
    db.add(
        EligibilityLookup(
            user_insurance_id=insurance.id,
            ran_at=datetime.utcnow(),
            is_claim_ready=True,
            mental_health_covered=True,
        )
    )
    appointment = Appointment(
        patient_id=patient.id,
        provider_id=provider.id,
        starts_at=datetime.utcnow(),
    )
    db.add(appointment)
    db.flush()

    confirmability = session_confirmability_service.get_confirmability(db, appointment)
    assert confirmability.is_confirmable is False
    assert {b.reason.value for b in confirmability.blockers} == {
        "PROVIDER_LICENSE_EXPIRED"
    }
