from ai.text.detector import detect_text
from ai.trust.engine import engine
from services.report_service import report_service


class TextService:

    def analyze(self, title: str, content: str):

        analysis_result = detect_text(title, content)

        trust_result = engine.analyze(analysis_result)

        file_info = {
            "file_id": None,
            "filename": "text_input"
        }

        report = report_service.build_report(
            file_info=file_info,
            analysis_result=analysis_result,
            trust_result=trust_result
        )

        return report


text_service = TextService()