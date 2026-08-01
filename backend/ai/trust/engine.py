from .risk import get_risk_level
from .recommendation import get_recommendation


class TrustEngine:

    def analyze(self, image_result: dict):

        prediction = image_result["prediction"]
        confidence = image_result["confidence"]

        if prediction == "Real":
            trust_score = round(confidence)

        else:
            trust_score = round(100 - confidence)

        risk_level = get_risk_level(trust_score)

        recommendation = get_recommendation(
            prediction,
            confidence,
            risk_level
        )

        return {
            "trust_score": trust_score,
            "risk_level": risk_level,
            "recommendation": recommendation
        }


engine = TrustEngine()