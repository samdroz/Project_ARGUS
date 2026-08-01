def get_recommendation(prediction: str,
                       confidence: float,
                       risk_level: str) -> str:

    if prediction == "Real":

        if risk_level == "LOW":
            return (
                "The uploaded image appears authentic. "
                "No significant signs of manipulation were detected."
            )

        return (
            "The image appears authentic, "
            "but further verification is recommended."
        )

    return (
        "Potential manipulation detected. "
        "Verify this image using additional evidence."
    )