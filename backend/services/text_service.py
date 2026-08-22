from typing import Dict, Any
from ai.text.detector import detect_text
from ai.text.analyzer import text_analyzer
from ai.fact_checker import fact_checker
from ai.trust.engine import engine
from services.report_service import report_service


class TextService:
    """
    Text analysis and factual claim verification service.
    """

    def analyze(self, title: str, content: str, verify_claims: bool = True) -> Dict[str, Any]:
        # 1. Model Stylistic & Misinformation Detection
        analysis_result = detect_text(title, content)

        # 2. Claim Extraction & Factual Evidence Retrieval
        evidence_result = None
        claims_list = []
        if verify_claims and content:
            extracted_claim_strings = text_analyzer.extract_claims(content, max_claims=3)
            evidence_result = fact_checker.verify_text_claims(extracted_claim_strings)
            claims_list = evidence_result.get("claims", [])

        # 3. Multi-Signal Trust Engine Evaluation
        trust_result = engine.analyze(
            analysis_result=analysis_result,
            evidence=evidence_result,
            claims=claims_list,
            metadata={"character_count": len(content), "word_count": len(content.split())}
        )

        file_info = {
            "file_id": None,
            "filename": "text_input"
        }

        # 4. Standardized Report
        report = report_service.build_report(
            media_type="text",
            analysis_result=analysis_result,
            trust_result=trust_result,
            file_info=file_info,
            evidence_result=evidence_result,
            claims=claims_list,
            metadata={
                "title": title,
                "character_count": len(content),
                "word_count": len(content.split())
            },
            processing_time_ms=analysis_result.get("processing_time_ms", 0.0)
        )

        return report


text_service = TextService()