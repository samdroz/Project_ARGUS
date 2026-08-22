from typing import Dict, Any
from ai.audio.detector import detect_audio
from ai.metadata.analyzer import metadata_analyzer
from ai.trust.engine import engine
from services.report_service import report_service


class AudioService:
    """
    Audio verification service for synthetic speech, deepfakes, and voice clones.
    """

    def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        audio_path = file_info["path"]

        # 1. AI & Acoustic Forensics
        audio_result = detect_audio(audio_path)

        # 2. Metadata
        metadata_result = metadata_analyzer.analyze(audio_path)
        metadata_result["duration_sec"] = audio_result.get("duration_sec")

        # 3. Trust Engine
        trust_result = engine.analyze(
            analysis_result=audio_result,
            forensics=audio_result.get("forensics"),
            metadata=metadata_result
        )

        # 4. Standardized Report
        report = report_service.build_report(
            media_type="audio",
            analysis_result=audio_result,
            trust_result=trust_result,
            file_info=file_info,
            metadata_result=metadata_result,
            forensics_result=audio_result.get("forensics"),
            processing_time_ms=audio_result.get("processing_time_ms", 0.0)
        )

        return report


audio_service = AudioService()
