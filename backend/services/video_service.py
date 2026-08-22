from typing import Dict, Any
from ai.video.analyzer import video_analyzer
from ai.metadata.analyzer import metadata_analyzer
from ai.trust.engine import engine
from services.report_service import report_service


class VideoService:
    """
    Service orchestration for video verification pipeline.
    """

    def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        video_path = file_info["path"]

        # 1. Temporal Video AI & Frame Forensics
        video_result = video_analyzer.analyze(video_path)

        # 2. Metadata Analysis
        metadata_result = metadata_analyzer.analyze(video_path)

        # 3. Trust Engine Analysis
        trust_result = engine.analyze(
            analysis_result=video_result,
            metadata=metadata_result
        )

        # 4. Standardized Report
        report = report_service.build_report(
            media_type="video",
            analysis_result=video_result,
            trust_result=trust_result,
            file_info=file_info,
            metadata_result=metadata_result,
            processing_time_ms=video_result.get("processing_time_ms", 0.0)
        )

        return report


video_service = VideoService()