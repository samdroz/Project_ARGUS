from .risk import get_risk_level
from .recommendation import get_recommendation


class TrustEngine:
    """
    Generates trust score, risk level and recommendation
    for any analysis result (image, video, text, audio, etc.)
    """

    def analyze(self, analysis_result: dict):

        prediction = analysis_result["prediction"]
        confidence = analysis_result["confidence"]
        media_type = analysis_result.get("media_type", "image")

        # Calculate Trust Score
        if prediction == "Real":
            trust_score = round(confidence)
        else:
            trust_score = round(100 - confidence)

        # Clamp between 0 and 100
        trust_score = max(0, min(100, trust_score))

        # Determine Risk Level
        risk_level = get_risk_level(trust_score)

        # Generate Recommendation
        recommendation = get_recommendation(
            prediction=prediction,
            confidence=confidence,
            risk_level=risk_level,
            media_type=media_type
        )

        return {
            "trust_score": trust_score,
            "risk_level": risk_level,
            "recommendation": recommendation
        }


engine = TrustEngine()