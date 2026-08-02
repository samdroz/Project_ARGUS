def get_recommendation(
    prediction: str,
    confidence: float,
    risk_level: str,
    media_type: str = "image"
) -> str:

    media = media_type.lower()

    # ---------- TEXT ----------
    if media == "text":

        if prediction == "Fake":

            if risk_level == "HIGH":
                return (
                    "The submitted text is highly likely to contain misinformation "
                    "or false claims. Verify it using trusted news sources before sharing."
                )

            elif risk_level == "MEDIUM":
                return (
                    "The submitted text may contain misleading information. "
                    "Cross-check it with reliable sources."
                )

            else:
                return (
                    "The submitted text shows minor signs of misinformation. "
                    "Additional verification is recommended."
                )

        else:

            if risk_level == "LOW":
                return (
                    "The submitted text appears credible based on the AI model's analysis."
                )

            elif risk_level == "MEDIUM":
                return (
                    "The submitted text appears mostly credible, "
                    "but independent verification is recommended."
                )

            else:
                return (
                    "The submitted text could not be verified with high confidence."
                )

    # ---------- IMAGE / VIDEO ----------

    if prediction == "Real":

        if risk_level == "LOW":
            return (
                f"The uploaded {media} appears authentic. "
                "No significant signs of manipulation were detected."
            )

        elif risk_level == "MEDIUM":
            return (
                f"The uploaded {media} appears authentic, "
                "but further verification is recommended."
            )

        else:
            return (
                f"The uploaded {media} could not be verified with high confidence."
            )

    else:

        if risk_level == "HIGH":
            return (
                f"The uploaded {media} is highly likely to be manipulated "
                "or AI-generated. Treat it with caution."
            )

        elif risk_level == "MEDIUM":
            return (
                f"The uploaded {media} shows possible signs of manipulation."
            )

        else:
            return (
                f"The uploaded {media} may contain manipulated content."
            )