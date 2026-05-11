from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.insurance.models.eligibility_lookup import EligibilityLookup
from app.modules.insurance.models.user_insurance import EligibilityStatus, UserInsurance


def run_lookup(
    db: Session,
    user_insurance: UserInsurance,
    *,
    is_claim_ready: bool,
    mental_health_covered: bool,
    notes: str = "",
) -> EligibilityLookup:
    """
    Record an eligibility lookup result for a UserInsurance.

    Also mirrors the latest claim-readiness state onto user_insurance.eligibility_status
    so callers that only have a UserInsurance row don't need to join through to the
    eligibility_lookups table for a quick check.
    """
    lookup = EligibilityLookup(
        user_insurance_id=user_insurance.id,
        ran_at=datetime.utcnow(),
        is_claim_ready=is_claim_ready,
        mental_health_covered=mental_health_covered,
        notes=notes,
    )
    db.add(lookup)

    if is_claim_ready and mental_health_covered:
        user_insurance.eligibility_status = EligibilityStatus.VERIFIED
    else:
        user_insurance.eligibility_status = EligibilityStatus.UNVERIFIED

    db.flush()
    return lookup
