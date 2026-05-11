from datetime import date

from sqlalchemy.orm import Session

from app.modules.insurance.repositories import (
    eligibility_lookup_repository,
    user_insurance_repository,
)
from app.modules.provider.repositories import provider_repository
from app.modules.provider.schemas.confirmability import (
    ConfirmabilityResponse,
    UnconfirmableBlocker,
    UnconfirmableReason,
)
from app.modules.scheduling.models.appointment import Appointment


def get_confirmability(
    db: Session, appointment: Appointment
) -> ConfirmabilityResponse:
    """
    Full pre-confirmation check for a specific appointment. Runs *every* time a
    provider clicks Confirm, so it goes to the source of truth for each input —
    no denormalized fields.

    Inputs considered:
      • The patient's latest eligibility lookup (claim-ready + MH coverage).
      • The provider's license expiration.
    """
    blockers: list[UnconfirmableBlocker] = []

    insurance = user_insurance_repository.get_active_for_patient(
        db, appointment.patient_id
    )
    if insurance is None:
        blockers.append(
            UnconfirmableBlocker(
                reason=UnconfirmableReason.PATIENT_MISSING_INSURANCE,
                message="Patient has no insurance on file.",
            )
        )
    else:
        lookup = eligibility_lookup_repository.latest_for_user_insurance(
            db, insurance.id
        )
        if lookup is None or not lookup.is_claim_ready:
            blockers.append(
                UnconfirmableBlocker(
                    reason=UnconfirmableReason.ELIGIBILITY_NOT_CLAIM_READY,
                    message=(
                        f"Eligibility for {insurance.carrier_name} is not claim-ready."
                    ),
                )
            )
        if lookup is not None and not lookup.mental_health_covered:
            blockers.append(
                UnconfirmableBlocker(
                    reason=UnconfirmableReason.MENTAL_HEALTH_NOT_COVERED,
                    message=(
                        f"{insurance.carrier_name} plan does not cover mental health."
                    ),
                )
            )

    provider = provider_repository.get(db, appointment.provider_id)
    if provider is not None and provider.license_expires_on < date.today():
        blockers.append(
            UnconfirmableBlocker(
                reason=UnconfirmableReason.PROVIDER_LICENSE_EXPIRED,
                message=(
                    f"Provider license in {provider.license_state} expired on "
                    f"{provider.license_expires_on.isoformat()}."
                ),
            )
        )

    return ConfirmabilityResponse(
        appointment_id=appointment.id,
        is_confirmable=not blockers,
        blockers=blockers,
    )
