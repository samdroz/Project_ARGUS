from ai.video.analyzer import video_analyzer
from ai.trust.engine import engine
from services.report_service import report_service


class VideoService:

    def analyze(self, file_info: dict):

        video_result = video_analyzer.analyze(file_info["path"])

        trust_result = engine.analyze(video_result)

        report = report_service.build_report(
            file_info=file_info,
            image_result=video_result,
            trust_result=trust_result
        )

        return report


video_service = VideoService()