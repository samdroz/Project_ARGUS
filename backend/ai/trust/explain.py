def generate_factors(
    prediction: str,
    confidence: float,
    media_type: str
) -> list[str]:

    factors = []

    if confidence >= 90:
        factors.append(
            "Very high model confidence."
        )

    elif confidence >= 75:
        factors.append(
            "Good model confidence."
        )

    elif confidence >= 50:
        factors.append(
            "Moderate model confidence."
        )

    else:
        factors.append(
            "Low model confidence."
        )

    if prediction == "Fake":

        factors.append(
            f"The AI model detected signs of manipulation in the {media_type}."
        )

    else:

        factors.append(
            f"The AI model found no major manipulation indicators."
        )

    factors.append(
        "This result is AI-assisted and should be verified if the content is sensitive."
    )

    return factors