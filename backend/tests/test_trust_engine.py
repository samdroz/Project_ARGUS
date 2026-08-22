import pytest
from ai.trust.engine import TrustEngine
from ai.trust.risk import get_risk_level


def test_trust_engine_insufficient_evidence():
    engine = TrustEngine()
    analysis_result = {
        "media_type": "text",
        "prediction": "Unverified",
        "confidence": 50.0,
        "model": "hamzab/roberta-fake-news-classification"
    }

    result = engine.analyze(analysis_result=analysis_result, evidence=None)

    # When there is no evidence and model is inconclusive, trust_score must be None
    assert result["trust_score"] is None
    assert result["risk_level"] == "INSUFFICIENT_EVIDENCE"
    assert result["verdict"] == "UNVERIFIED"
    assert len(result["factors"]) > 0
    assert len(result["limitations"]) > 0


def test_trust_engine_supported_evidence():
    engine = TrustEngine()
    analysis_result = {
        "media_type": "text",
        "prediction": "Real",
        "confidence": 90.0,
        "model": "hamzab/roberta-fake-news-classification"
    }
    evidence = {
        "status": "SUPPORTED",
        "sources_count": 3
    }

    result = engine.analyze(analysis_result=analysis_result, evidence=evidence)

    assert result["trust_score"] is not None
    assert result["trust_score"] >= 80
    assert result["risk_level"] == "LOW"
    assert result["verdict"] == "SUPPORTED"


def test_trust_engine_contradicted_evidence():
    engine = TrustEngine()
    analysis_result = {
        "media_type": "text",
        "prediction": "Fake",
        "confidence": 92.0,
        "model": "hamzab/roberta-fake-news-classification"
    }
    evidence = {
        "status": "CONTRADICTED",
        "sources_count": 2
    }

    result = engine.analyze(analysis_result=analysis_result, evidence=evidence)

    assert result["trust_score"] is not None
    assert result["trust_score"] <= 25
    assert result["risk_level"] in ("HIGH", "CRITICAL")
    assert result["verdict"] == "CONTRADICTED"


def test_trust_engine_image_forensics_integration():
    engine = TrustEngine()
    analysis_result = {
        "media_type": "image",
        "prediction": "Fake",
        "confidence": 88.0,
        "model": "Wvolf/ViT_Deepfake_Detection"
    }
    forensics = {
        "ela": {"splicing_risk": "HIGH"},
        "frequency_analysis": {"is_synthetic_noise_pattern": True}
    }

    result = engine.analyze(analysis_result=analysis_result, forensics=forensics)

    assert result["trust_score"] is not None
    assert result["trust_score"] <= 25
    assert result["risk_level"] in ("HIGH", "CRITICAL")
    assert result["verdict"] == "FAKE"


def test_risk_level_mapping():
    assert get_risk_level(90) == "LOW"
    assert get_risk_level(65) == "MEDIUM"
    assert get_risk_level(30) == "HIGH"
    assert get_risk_level(10) == "CRITICAL"
    assert get_risk_level(None) == "INSUFFICIENT_EVIDENCE"
