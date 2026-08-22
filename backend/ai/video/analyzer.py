import time
from statistics import mean
from typing import Dict, Any, List

from .extractor import extractor
from .detector import video_detector
from utils.logger import logger


class VideoAnalyzer:
    """
    Temporal video analyzer that aggregates frame-level forensic and deepfake signals.
    """

    def analyze(self, video_path: str) -> Dict[str, Any]:
        start_time = time.perf_counter()

        extraction_result = extractor.extract(video_path)
        temp_dir = extraction_result["temp_dir"]
        frames_meta = extraction_result["frames"]

        try:
            frame_results = video_detector.analyze_frames(frames_meta)

            total_frames = len(frame_results)
            predictions = [f["prediction"] for f in frame_results]
            confidences = [f["confidence"] for f in frame_results]

            real_frames = [f for f in frame_results if f["prediction"] == "Real"]
            fake_frames = [f for f in frame_results if f["prediction"] == "Fake"]

            num_real = len(real_frames)
            num_fake = len(fake_frames)
            fake_ratio = num_fake / max(1, total_frames)

            # Detect suspicious bursts (consecutive fake frames or high-confidence fake frames)
            high_conf_fakes = [f for f in fake_frames if f["confidence"] >= 75.0]

            if num_fake >= 2 or fake_ratio >= 0.20 or len(high_conf_fakes) >= 1:
                overall_prediction = "Fake"
                if high_conf_fakes:
                    overall_confidence = round(mean([f["confidence"] for f in high_conf_fakes]), 2)
                else:
                    overall_confidence = round(mean([f["confidence"] for f in fake_frames]), 2)
            else:
                overall_prediction = "Real"
                overall_confidence = round(mean([f["confidence"] for f in real_frames]), 2) if real_frames else 60.0

            # Collect suspicious frame timestamps
            suspicious_frames_summary = [
                {
                    "frame_no": f["frame_no"],
                    "timestamp_sec": f["timestamp_sec"],
                    "confidence": f["confidence"],
                    "face_detected": f["face_detected"]
                }
                for f in fake_frames
            ]

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            models_used = list(set([f.get("model", "Unknown") for f in frame_results]))
            primary_model = models_used[0] if models_used else "ViT + Frame Forensics"

            return {
                "media_type": "video",
                "prediction": overall_prediction,
                "confidence": overall_confidence,
                "frames_analyzed": total_frames,
                "real_frames": num_real,
                "fake_frames": num_fake,
                "fake_frame_ratio": round(fake_ratio, 3),
                "duration_sec": extraction_result["duration_sec"],
                "fps": extraction_result["fps"],
                "suspicious_frames": suspicious_frames_summary,
                "model": primary_model,
                "processing_time_ms": elapsed_ms
            }

        finally:
            # Clean up temporary frame files
            extractor.cleanup(temp_dir)


video_analyzer = VideoAnalyzer()