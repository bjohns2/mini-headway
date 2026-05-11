import enum

from pydantic import BaseModel


class UnconfirmableReason(str, enum.Enum):
    PATIENT_MISSING_INSURANCE = "PATIENT_MISSING_INSURANCE"
    ELIGIBILITY_NOT_CLAIM_READY = "ELIGIBILITY_NOT_CLAIM_READY"
    MENTAL_HEALTH_NOT_COVERED = "MENTAL_HEALTH_NOT_COVERED"
    PROVIDER_LICENSE_EXPIRED = "PROVIDER_LICENSE_EXPIRED"


class UnconfirmableBlocker(BaseModel):
    reason: UnconfirmableReason
    message: str


class ConfirmabilityResponse(BaseModel):
    appointment_id: int
    is_confirmable: bool
    blockers: list[UnconfirmableBlocker]
