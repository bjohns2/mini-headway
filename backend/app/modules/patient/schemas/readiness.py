import enum

from pydantic import BaseModel


class ReadinessIssueType(str, enum.Enum):
    MISSING_INSURANCE = "MISSING_INSURANCE"
    INSURANCE_TERMINATED = "INSURANCE_TERMINATED"
    INSURANCE_NOT_VERIFIED = "INSURANCE_NOT_VERIFIED"


class ReadinessIssue(BaseModel):
    type: ReadinessIssueType
    message: str


class PatientReadinessResponse(BaseModel):
    patient_id: int
    is_ready: bool
    issues: list[ReadinessIssue]
