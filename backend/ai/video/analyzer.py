from statistics import mean

from .extractor import extractor
from .detector import video_detector


class VideoAnalyzer:

    def analyze(self, video_path):

        frames = extractor.extract(
            video_path,
            "frames"
        )

        result = video_detector.analyze_frames(frames)

        predictions = result["predictions"]
        confidences = result["confidences"]

        real_frames = predictions.count("Real")
        fake_frames = predictions.count("Fake")

        prediction = (
            "Real"
            if real_frames >= fake_frames
            else "Fake"
        )

        confidence = round(mean(confidences), 2)

        return {

            "prediction": prediction,

            "confidence": confidence,

            "frames_analyzed": len(frames),

            "real_frames": real_frames,

            "fake_frames": fake_frames

        }


video_analyzer = VideoAnalyzer()