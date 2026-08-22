from typing import Dict, Any
from ai.image.detector import detect_image
from ai.metadata.analyzer import metadata_analyzer
from ai.trust.engine import engine
from services.report_service import report_service


class ImageService:
    """
    Service orchestration for image verification pipeline.
    """

    def analyze(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        image_path = file_info["path"]

        # 1. AI Vision Model & Digital Forensics
        image_result = detect_image(image_path)

        # 2. Metadata Analysis
        metadata_result = metadata_analyzer.analyze(image_path)

        # 3. Multi-Signal Trust Engine
        trust_result = engine.analyze(
            analysis_result=image_result,
            forensics=image_result.get("forensics"),
            metadata=metadata_result
        )

        # 4. Standardized Report
        report = report_service.build_report(
            media_type="image",
            analysis_result=image_result,
            trust_result=trust_result,
            file_info=file_info,
            metadata_result=metadata_result,
            forensics_result=image_result.get("forensics"),
            processing_time_ms=image_result.get("processing_time_ms", 0.0)
        )

        return report


image_service = ImageService()