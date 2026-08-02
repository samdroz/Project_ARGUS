class ReportService:

    def build_report(
        self,
        file_info: dict,
        analysis_result: dict,
        trust_result: dict
    ):

        return {
            "status": "success",

            "file": {
                "id": file_info["file_id"],
                "name": file_info["filename"]
            },

            "analysis": {
                **analysis_result,
                **trust_result
            }
        }


report_service = ReportService()