import uuid
from typing import Dict, Any, Optional, List


class ReportService:
    """
    Standardized report generator for all Project ARGUS verification pipelines.
    """

    def build_report(
        self,
        media_type: str,
        analysis_result: Dict[str, Any],
        trust_result: Dict[str, Any],
        file_info: Optional[Dict[str, Any]] = None,
        metadata_result: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        evidence_result: Optional[Dict[str, Any]] = None,
        evidence: Optional[Dict[str, Any]] = None,
        claims: Optional[List[Dict[str, Any]]] = None,
        forensics_result: Optional[Dict[str, Any]] = None,
        forensics: Optional[Dict[str, Any]] = None,
        processing_time_ms: float = 0.0
    ) -> Dict[str, Any]:
        """
        Construct a complete, unified response matching the StandardResponse schema.
        """
        analysis_id = str(uuid.uuid4())

        prediction = analysis_result.get("prediction", "Unverified")
        confidence = analysis_result.get("confidence", 0.0)
        model_name = analysis_result.get("model", "ARGUS Engine")
        device_name = analysis_result.get("device", "cpu")

        trust_score = trust_result.get("trust_score")  # Can be None / int
        risk_level = trust_result.get("risk_level", "UNKNOWN")
        verdict = trust_result.get("verdict", prediction.upper())
        factors = trust_result.get("factors", [])
        recommendation = trust_result.get("recommendation", "")
        limitations = trust_result.get("limitations", [])

        meta_dict = metadata_result if metadata_result is not None else (metadata or {})
        evi_dict = evidence_result if evidence_result is not None else evidence
        for_dict = forensics_result if forensics_result is not None else (forensics or analysis_result.get("forensics", {}))

        # File block
        file_block = None
        if file_info:
            file_block = {
                "id": file_info.get("file_id"),
                "name": file_info.get("filename"),
                "saved_filename": file_info.get("saved_filename"),
                "path": file_info.get("path")
            }

        return {
            "status": "success",
            "analysis_id": analysis_id,
            "media_type": media_type,
            "verdict": verdict,
            "prediction": prediction,
            "confidence": confidence,
            "trust_score": trust_score,
            "risk_level": risk_level,
            "model": model_name,
            "file": file_block,
            "analysis": analysis_result,
            "evidence": evi_dict,
            "claims": claims or [],
            "metadata": meta_dict,
            "forensics": for_dict,
            "trust": {
                "score": trust_score,
                "risk": risk_level,
                "verdict": verdict,
                "recommendation": recommendation,
                "factors": factors,
                "limitations": limitations
            },
            "factors": factors,
            "recommendation": recommendation,
            "limitations": limitations,
            "processing": {
                "time_ms": processing_time_ms or analysis_result.get("processing_time_ms", 0.0),
                "device": device_name,
                "model": model_name
            }
        }


report_service = ReportService()