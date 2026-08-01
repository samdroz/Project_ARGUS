class ReportService:

    def build_report(
        self,
        file_info: dict,
        image_result: dict,
        trust_result: dict
    ):

        return {
            "status": "success",

            "file": {
                "id": file_info["file_id"],
                "name": file_info["filename"]
            },

            "analysis": {
                **image_result,
                **trust_result
            }
        }


report_service = ReportService()