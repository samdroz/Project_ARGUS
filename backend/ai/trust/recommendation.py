from typing import Optional


def get_recommendation(
    prediction: str,
    confidence: float,
    risk_level: str,
    verdict: str,
    media_type: str = "text"
) -> str:
    """
    Produce calibrated, actionable recommendation for users and moderators.
    """
    media = media_type.lower()

    if risk_level == "INSUFFICIENT_EVIDENCE" or verdict == "UNVERIFIED":
        return (
            f"The authenticity of this {media} could not be definitively established. "
            "Independent cross-referencing with primary sources is required before taking action or sharing."
        )

    if risk_level == "CRITICAL" or verdict == "CONTRADICTED":
        return (
            f"High risk of misinformation/manipulation. The submitted {media} exhibits strong contradiction with factual records "
            "or severe manipulation artifacts. Do not amplify or treat as factual without verified correction."
        )

    if risk_level == "HIGH":
        if media in ("image", "video", "audio"):
            return (
                f"Elevated manipulation indicators detected in this {media}. "
                "Inspect individual forensic factors and seek original source files."
            )
        else:
            return (
                "The text exhibits sensationalist misinformation markers or uncorroborated claims. "
                "Verify through official newsrooms or fact-checkers."
            )

    if risk_level == "MEDIUM":
        return (
            f"The {media} contains mixed or moderate credibility signals. "
            "Exercise caution and verify key claims or imagery against known primary sources."
        )

    if risk_level == "LOW" or verdict in ("SUPPORTED", "VERIFIED"):
        return (
            f"The {media} appears credible and authentic based on available evidence and forensic analysis. "
            "No significant indicators of manipulation or false claims were found."
        )

    return f"Review the detailed factors and sources for this {media}."