import time
from typing import Dict, Any

from ai.url.validator import is_safe_url
from ai.url.extractor import url_extractor
from ai.url.classifier import url_classifier
from ai.text.detector import detect_text
from ai.text.analyzer import text_analyzer
from ai.fact_checker import fact_checker
from ai.trust.engine import engine
from services.report_service import report_service


class URLService:
    """
    Complete URL verification service with SSRF security, content extraction,
    claim verification, and Trust Engine scoring.
    """

    def analyze(self, url: str, verify_claims: bool = True) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # 1. SSRF Validation
        is_safe, reason = is_safe_url(url)
        if not is_safe:
            raise ValueError(f"Security Alert - SSRF Violation: {reason}")

        # 2. Content Extraction
        content_data = url_extractor.extract_content(url)
        domain = content_data["domain"]
        title = content_data["title"]
        body = content_data["content"]

        # 3. Source Classification
        source_class = url_classifier.classify(domain)

        # 4. Text / Misinformation Analysis on Article Content
        text_result = detect_text(title=title, content=body)

        # 5. Claim Extraction & Evidence Retrieval
        evidence_result = None
        claims_list = []
        if verify_claims and body:
            extracted_claim_strings = text_analyzer.extract_claims(body, max_claims=3)
            evidence_result = fact_checker.verify_text_claims(extracted_claim_strings)
            claims_list = evidence_result.get("claims", [])

        # 6. Trust Engine Assessment
        trust_result = engine.analyze(
            analysis_result=text_result,
            evidence=evidence_result,
            claims=claims_list,
            metadata={
                "domain": domain,
                "source_type": source_class.get("source_type"),
                "source_quality": source_class.get("source_quality"),
                "role": source_class.get("role")
            }
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # 7. Standardized Report
        report = report_service.build_report(
            media_type="url",
            analysis_result={
                **text_result,
                "url": url,
                "domain": domain,
                "title": title,
                "source_classification": source_class
            },
            trust_result=trust_result,
            evidence_result=evidence_result,
            claims=claims_list,
            metadata={
                "url": url,
                "domain": domain,
                "source_classification": source_class,
                "content_length": content_data.get("content_length", 0)
            },
            processing_time_ms=elapsed_ms
        )

        return report


url_service = URLService()
