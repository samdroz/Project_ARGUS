from typing import Dict, Any, Optional, List

from .risk import get_risk_level
from .recommendation import get_recommendation
from .explain import generate_factors, generate_limitations


class TrustEngine:
    """
    Multi-signal, calibrated Trust Engine for Project ARGUS.
    Combines model inference, factual evidence retrieval, digital forensics,
    source quality, and metadata without fabricating scores.
    """

    def analyze(
        self,
        analysis_result: Dict[str, Any],
        evidence: Optional[Dict[str, Any]] = None,
        forensics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        claims: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all multimodal signals and compute calibrated trust metrics.
        """
        media_type = analysis_result.get("media_type", "image").lower()
        prediction = analysis_result.get("prediction", "Unverified")
        confidence = float(analysis_result.get("confidence", 50.0))
        model_name = analysis_result.get("model", "")
        is_fallback = "fallback" in model_name.lower() or "deterministic" in model_name.lower()

        forensics = forensics or analysis_result.get("forensics")
        evidence_status = evidence.get("status", "UNVERIFIED") if evidence else "UNVERIFIED"
        sources_count = evidence.get("sources_count", 0) if evidence else 0

        trust_score: Optional[int] = None
        verdict: str = "UNVERIFIED"

        # -------------------------------------------------------------
        # 1. TEXT & URL VERIFICATION (Fact-driven + Stylistic Model)
        # -------------------------------------------------------------
        if media_type in ("text", "url"):
            # Check if we have active claim/external evidence
            if evidence and evidence_status != "UNVERIFIED" and sources_count > 0:
                if evidence_status == "SUPPORTED":
                    # Verified by external evidence
                    base = 85.0
                    bonus = min(12.0, sources_count * 3.0)
                    trust_score = int(min(98, round(base + bonus)))
                    verdict = "SUPPORTED"
                elif evidence_status == "CONTRADICTED":
                    # Refuted by external evidence
                    penalty = min(20.0, sources_count * 5.0)
                    trust_score = int(max(5, round(25 - penalty)))
                    verdict = "CONTRADICTED"
                elif evidence_status == "MIXED":
                    trust_score = 50
                    verdict = "MIXED"
            else:
                # No external evidence found
                if prediction == "Fake" and confidence >= 85:
                    # Stylistic misinformation markers are strong
                    trust_score = int(max(15, round(100 - confidence)))
                    verdict = "UNVERIFIED_SUSPICIOUS"
                elif prediction == "Real" and confidence >= 85:
                    # Text appears well-formed, but unverified factually
                    trust_score = int(min(75, round(confidence * 0.75)))
                    verdict = "UNVERIFIED_CREDIBLE_STYLE"
                else:
                    # Inconclusive
                    trust_score = None
                    verdict = "UNVERIFIED"

        # -------------------------------------------------------------
        # 2. IMAGE, VIDEO, AUDIO VERIFICATION (Forensics + Neural Model)
        # -------------------------------------------------------------
        else:
            # Model score component (0 to 100 authenticity)
            model_authenticity = confidence if prediction == "Real" else (100.0 - confidence)

            # Forensic score component
            forensic_authenticity = 50.0
            if forensics:
                splicing = forensics.get("ela", {}).get("splicing_risk", "LOW")
                is_synthetic = forensics.get("frequency_analysis", {}).get("is_synthetic_noise_pattern", False)

                if splicing == "HIGH" or is_synthetic:
                    forensic_authenticity = 15.0
                elif splicing == "MEDIUM":
                    forensic_authenticity = 40.0
                elif splicing == "LOW" and not is_synthetic:
                    forensic_authenticity = 85.0

                # Audio specific
                if "unnatural_pitch_stability" in forensics:
                    if forensics.get("unnatural_pitch_stability") or forensics.get("spectral_discontinuity"):
                        forensic_authenticity = min(forensic_authenticity, 20.0)
                    else:
                        forensic_authenticity = max(forensic_authenticity, 80.0)

            # Metadata score component
            meta_score = 50.0
            if metadata:
                if metadata.get("editing_software"):
                    meta_score = 35.0  # mild caution, not full penalty
                elif metadata.get("has_exif"):
                    meta_score = 70.0

            # Calibrated blend
            if is_fallback:
                # Weighted heavily on forensics
                final_score = (0.80 * forensic_authenticity) + (0.20 * meta_score)
            else:
                final_score = (0.55 * model_authenticity) + (0.35 * forensic_authenticity) + (0.10 * meta_score)

            trust_score = int(max(0, min(100, round(final_score))))

            if trust_score >= 75:
                verdict = "REAL"
            elif trust_score <= 35:
                verdict = "FAKE"
            else:
                verdict = "SUSPICIOUS"

        # -------------------------------------------------------------
        # 3. Risk Level, Factors, Recommendations, Limitations
        # -------------------------------------------------------------
        risk_level = get_risk_level(trust_score)

        factors = generate_factors(
            prediction=prediction,
            confidence=confidence,
            media_type=media_type,
            evidence=evidence,
            forensics=forensics,
            metadata=metadata,
            claims=claims
        )

        limitations = generate_limitations(
            media_type=media_type,
            evidence=evidence,
            is_fallback_model=is_fallback
        )

        recommendation = get_recommendation(
            prediction=prediction,
            confidence=confidence,
            risk_level=risk_level,
            verdict=verdict,
            media_type=media_type
        )

        return {
            "trust_score": trust_score,
            "risk_level": risk_level,
            "verdict": verdict,
            "confidence": round(confidence, 2),
            "factors": factors,
            "limitations": limitations,
            "recommendation": recommendation
        }


engine = TrustEngine()