import pytest
from ai.text.analyzer import text_analyzer
from ai.text.detector import detect_text
from ai.text.preprocess import prepare_text


def test_text_stylistic_analysis():
    sensational_text = "SHOCKING TRUTH REVEALED!!! YOU WON'T BELIEVE WHAT HAPPENED TODAY!"
    signals = text_analyzer.analyze_style(sensational_text)

    assert signals["all_caps_ratio"] > 0.5
    assert signals["exclamation_count"] >= 3
    assert signals["sensationalism_score"] > 50
    assert len(signals["clickbait_flags"]) > 0


def test_text_claim_extraction():
    article = (
        "The World Health Organization officially confirmed a new malaria vaccine. "
        "Global clinical trials showed a 75 percent reduction in severe cases. "
        "Distribution is planned to begin early next year across several regions."
    )
    claims = text_analyzer.extract_claims(article, max_claims=3)
    assert len(claims) == 3
    assert "malaria vaccine" in claims[0]


def test_text_detection_execution():
    result = detect_text(
        title="Scientific Breakthrough in Renewable Fusion Energy",
        content="Physicists at the national laboratory achieved positive net energy gain in magnetic confinement experiments."
    )
    assert result["media_type"] == "text"
    assert result["prediction"] in ("Real", "Fake", "Unverified")
    assert result["confidence"] > 0
    assert "model" in result
