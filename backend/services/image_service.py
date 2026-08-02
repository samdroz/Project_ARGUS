from ai.image.detecter import detect_image
from ai.metadata.analyzer import metadata_analyzer
from ai.trust.engine import engine


class ImageService:

    def analyze(self, file_info: dict):

        image_path = file_info["path"]

        # AI Detection
        image_result = detect_image(image_path)

        # Metadata Analysis
        metadata_result = metadata_analyzer.analyze(image_path)

        # Trust Analysis
        trust_result = engine.analyze(image_result)

        return {
            "status": "success",
            "file": {
                "id": file_info["file_id"],
                "name": file_info["filename"]
            },
            "analysis": {
                **image_result,
                **trust_result
            },
            "metadata": metadata_result
        }


image_service = ImageService()