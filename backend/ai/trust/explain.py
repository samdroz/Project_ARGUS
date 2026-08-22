from typing import List, Dict, Any, Optional


def generate_factors(
    prediction: str,
    confidence: float,
    media_type: str,
    evidence: Optional[Dict[str, Any]] = None,
    forensics: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    claims: Optional[List[Dict[str, Any]]] = None
) -> List[str]:
    """
    Generate truthful, observation-grounded explainability factors.
    Every factor corresponds directly to a signal detected by the system.
    """
    factors = []

    # 1. Model confidence factor
    if confidence >= 90:
        factors.append(f"High-confidence model signal ({confidence:.1f}%) indicating {prediction.lower()} content.")
    elif confidence >= 70:
        factors.append(f"Moderate model confidence ({confidence:.1f}%) leaning toward {prediction.lower()}.")
    elif confidence > 0:
        factors.append(f"Low or tentative model confidence ({confidence:.1f}%).")

    # 2. Forensic signals
    if forensics:
        ela = forensics.get("ela", {})
        splicing = ela.get("splicing_risk")
        if splicing in ("HIGH", "MEDIUM"):
            factors.append(f"Error Level Analysis (ELA) detected elevated compression inconsistency ({splicing} risk), indicating possible local splicing.")

        freq = forensics.get("frequency_analysis", {})
        if freq.get("is_synthetic_noise_pattern"):
            factors.append("Frequency spectrum analysis identified unnatural high-frequency patterns consistent with AI synthesis.")

        # Audio forensics
        if "spectral_centroid_hz" in forensics:
            if forensics.get("spectral_discontinuity"):
                factors.append("Acoustic analysis detected abrupt spectral discontinuities characteristic of voice splicing.")
            if forensics.get("unnatural_pitch_stability"):
                factors.append("Acoustic analysis observed abnormally rigid pitch stability common in synthetic text-to-speech vocoders.")

    # 3. Metadata signals
    if metadata:
        if metadata.get("editing_software"):
            software = metadata.get("editing_software")
            factors.append(f"File metadata indicates processing with editing software ({software}).")
        if metadata.get("has_exif") and metadata.get("camera_make"):
            make = metadata.get("camera_make")
            model = metadata.get("camera_model", "")
            factors.append(f"Original camera hardware metadata present ({make} {model}).")

    # 4. External Evidence & Fact-checking signals
    if evidence:
        status = evidence.get("status", "UNVERIFIED")
        sources_count = evidence.get("sources_count", 0)

        if status == "SUPPORTED":
            factors.append(f"External fact-checking corroborated key claims across {sources_count} independent source(s).")
        elif status == "CONTRADICTED":
            factors.append(f"External evidence directly contradicts the submitted claim(s) based on {sources_count} authoritative source(s).")
        elif status == "MIXED":
            factors.append(f"External evidence is mixed; conflicting reporting found across {sources_count} sources.")
        elif status == "UNVERIFIED" and sources_count == 0:
            factors.append("No independent external sources could verify or disprove the specific claims.")

    # 5. Claim-level signals
    if claims:
        contra_claims = [c for c in claims if c.get("verdict") == "CONTRADICTED"]
        supp_claims = [c for c in claims if c.get("verdict") == "SUPPORTED"]
        if contra_claims:
            factors.append(f"{len(contra_claims)} extracted claim(s) refuted by reliable public evidence.")
        if supp_claims:
            factors.append(f"{len(supp_claims)} extracted claim(s) confirmed by reliable public evidence.")

    if not factors:
        factors.append("Preliminary automated inspection completed with baseline metrics.")

    return factors


def generate_limitations(
    media_type: str,
    evidence: Optional[Dict[str, Any]] = None,
    is_fallback_model: bool = False
) -> List[str]:
    """
    State honest boundaries and limitations of the verification result.
    """
    limitations = []

    if media_type in ("text", "url"):
        limitations.append("Linguistic/stylistic AI classifiers evaluate writing style and sensationalism, not real-time factual reality.")
        if not evidence or evidence.get("status") == "UNVERIFIED":
            limitations.append("Factual verification is limited by available search provider indices and public records.")

    if media_type in ("image", "video"):
        limitations.append("Vision AI models are trained on specific deepfake artifacts and may underperform on heavily compressed or novel diffusion techniques.")
        limitations.append("Missing camera EXIF or standard social media re-compression is not definitive proof of manipulation.")

    if media_type == "audio":
        limitations.append("Acoustic forensic metrics assess synthetic voice characteristics; background noise and lossy codecs may impact accuracy.")

    if is_fallback_model:
        limitations.append("Neural classifier was offline/unavailable; result was generated using deterministic forensic signal analyzers.")

    return limitations