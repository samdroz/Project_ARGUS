from typing import List, Dict, Any
from ai.image.detector import detect_image


class VideoDetector:
    """
    Performs frame-by-frame deepfake and forensic detection.
    """

    def analyze_frames(self, frames_meta: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze extracted video frames and collect per-frame findings.
        """
        results = []

        for frame in frames_meta:
            frame_path = frame["path"]
            frame_no = frame["frame_no"]
            timestamp_sec = frame["timestamp_sec"]

            detection = detect_image(frame_path)

            results.append({
                "frame_no": frame_no,
                "timestamp_sec": timestamp_sec,
                "prediction": detection.get("prediction", "Real"),
                "confidence": detection.get("confidence", 50.0),
                "face_detected": detection.get("face_detected", False),
                "model": detection.get("model", "Unknown"),
                "forensics": detection.get("forensics", {})
            })

        return results


video_detector = VideoDetector()