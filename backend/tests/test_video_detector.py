import os
from ai.video.analyzer import video_analyzer


def test_video_analyzer_execution():
    sample_path = os.path.join(os.path.dirname(__file__), "test.mp4")
    if os.path.exists(sample_path):
        res = video_analyzer.analyze(sample_path)
        assert res["media_type"] == "video"
        assert res["prediction"] in ("Real", "Fake")
        assert res["frames_analyzed"] > 0