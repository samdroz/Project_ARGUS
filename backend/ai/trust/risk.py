def get_risk_level(trust_score: int) -> str:
    """
    Convert trust score into a risk level.
    """

    if trust_score >= 80:
        return "LOW"

    elif trust_score >= 50:
        return "MEDIUM"

    return "HIGH"