from typing import Optional


def get_risk_level(trust_score: Optional[int]) -> str:
    """
    Convert calibrated trust score into a risk level.
    If trust_score is None, returns 'INSUFFICIENT_EVIDENCE'.
    """
    if trust_score is None:
        return "INSUFFICIENT_EVIDENCE"

    if trust_score >= 80:
        return "LOW"
    elif trust_score >= 50:
        return "MEDIUM"
    elif trust_score >= 20:
        return "HIGH"
    else:
        return "CRITICAL"