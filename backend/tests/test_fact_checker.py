import pytest
from ai.fact_checker import FactChecker, MockSearchProvider
from config.constants import EvidenceDirection, ClaimVerdict


def test_fact_checker_stance_evaluation():
    checker = FactChecker()

    contradict_stance = checker.evaluate_stance(
        claim_text="Scientists discovered alien city on Mars",
        source_snippet="Fact check: Scientists debunk viral hoax claiming an alien city was discovered on Mars.",
        source_title="Fact Check: False claim regarding Mars discovery"
    )
    assert contradict_stance == EvidenceDirection.CONTRADICTS

    support_stance = checker.evaluate_stance(
        claim_text="James Webb Telescope captures distant galaxy",
        source_snippet="NASA officially announced and confirmed new deep-field observations from the James Webb Space Telescope.",
        source_title="NASA confirmed new James Webb discovery"
    )
    assert support_stance == EvidenceDirection.SUPPORTS


def test_fact_checker_mock_provider_verification():
    mock_data = {
        "climate agreement": [
            {
                "title": "Global Climate Agreement Formally Confirmed",
                "url": "https://reuters.com/world/climate-agreement-confirmed",
                "domain": "reuters.com",
                "snippet": "Delegates officially confirmed the passage of the landmark climate agreement.",
                "source_type": "reputable_news",
                "source_quality": "HIGH"
            }
        ],
        "fake miracle cure": [
            {
                "title": "Debunk: Unproven miracle cure is a dangerous hoax",
                "url": "https://snopes.com/fact-check/miracle-cure-debunk",
                "domain": "snopes.com",
                "snippet": "False: Medical authorities debunk claims of a secret miracle cure.",
                "source_type": "fact-checker",
                "source_quality": "VERY_HIGH"
            }
        ]
    }

    provider = MockSearchProvider(mock_data)
    checker = FactChecker(provider=provider)

    # 1. Verify supported claim
    res_supp = checker.verify_claim(1, "Global climate agreement confirmed")
    assert res_supp["verdict"] == ClaimVerdict.SUPPORTED
    assert len(res_supp["sources"]) == 1

    # 2. Verify contradicted claim
    res_contra = checker.verify_claim(2, "Secret fake miracle cure discovered")
    assert res_contra["verdict"] == ClaimVerdict.CONTRADICTED
    assert len(res_contra["sources"]) == 1

    # 3. Verify unverified claim (empty mock)
    res_unv = checker.verify_claim(3, "Unrelated obscure rumor")
    assert res_unv["verdict"] == ClaimVerdict.UNVERIFIED
    assert len(res_unv["sources"]) == 0
