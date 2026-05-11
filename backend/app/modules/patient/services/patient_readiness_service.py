from sqlalchemy.orm import Session

from app.modules.insurance.models.user_insurance import EligibilityStatus
from app.modules.insurance.repositories import user_insurance_repository
from app.modules.patient.schemas.readiness import (
    PatientReadinessResponse,
    ReadinessIssue,
    ReadinessIssueType,
)


def compute_readiness(db: Session, patient_id: int) -> PatientReadinessResponse:
    """
    Quick top-of-screen readiness check for a patient — drives the Ready/Not-ready
    badge shown in the day view and on the appointment page.

    Reads denormalized state on the user_insurance row so that the day view can
    fan out across many patients without joining through to eligibility_lookups
    for each one.
    """
    issues: list[ReadinessIssue] = []

    insurance = user_insurance_repository.get_active_for_patient(db, patient_id)
    if insurance is None:
        issues.append(
            ReadinessIssue(
                type=ReadinessIssueType.MISSING_INSURANCE,
                message="Patient has no insurance on file.",
            )
        )
    elif insurance.eligibility_status == EligibilityStatus.TERMINATED:
        issues.append(
            ReadinessIssue(
                type=ReadinessIssueType.INSURANCE_TERMINATED,
                message=f"Coverage with {insurance.carrier_name} has been terminated.",
            )
        )
    elif insurance.eligibility_status != EligibilityStatus.VERIFIED:
        issues.append(
            ReadinessIssue(
                type=ReadinessIssueType.INSURANCE_NOT_VERIFIED,
                message=f"Coverage with {insurance.carrier_name} has not been verified.",
            )
        )

    return PatientReadinessResponse(
        patient_id=patient_id,
        is_ready=not issues,
        issues=issues,
    )
