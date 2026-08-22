import os
from ai.image.detector import detector


def test_detector_with_sample_image():
    sample_path = os.path.join(os.path.dirname(__file__), "test.jpg")
    if os.path.exists(sample_path):
        result = detector.predict(sample_path)
        assert result["media_type"] == "image"
        assert result["prediction"] in ("Real", "Fake")
        assert result["confidence"] > 0