import os
from ai.video.extractor import extractor


def test_video_frame_extraction():
    sample_path = os.path.join(os.path.dirname(__file__), "test.mp4")
    if os.path.exists(sample_path):
        res = extractor.extract(sample_path, max_frames=5)
        temp_dir = res["temp_dir"]
        try:
            assert len(res["frames"]) > 0
            assert res["fps"] > 0
        finally:
            extractor.cleanup(temp_dir)