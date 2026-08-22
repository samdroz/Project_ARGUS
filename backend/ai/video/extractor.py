import cv2
import os
import shutil
import tempfile
import math
from typing import List, Dict, Any

from config.settings import settings
from utils.logger import logger


class FrameExtractor:
    """
    Safe, isolated video frame extractor with interval sampling,
    duration caps, and automatic temporary directory management.
    """

    def extract(
        self,
        video_path: str,
        max_frames: int = None,
        frame_interval: int = None
    ) -> Dict[str, Any]:
        """
        Extract sampled frames from video into an isolated temporary folder.

        Returns:
            Dict containing:
                - 'temp_dir': path to temporary folder
                - 'fps': video frame rate
                - 'total_video_frames': total frame count in file
                - 'duration_sec': length of video in seconds
                - 'frames': list of dicts with frame metadata and file paths
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at {video_path}")

        max_frames = max_frames or settings.VIDEO_MAX_FRAMES
        default_interval = frame_interval or settings.VIDEO_FRAME_INTERVAL

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Unable to open or decode video stream.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if not fps or fps <= 0 or math.isnan(fps):
            fps = 30.0  # safe default fallback

        duration_sec = round(total_video_frames / fps, 2) if total_video_frames > 0 else 0.0

        # Calculate sampling step
        step = max(1, int(fps)) if default_interval is None else max(1, int(default_interval))
        if total_video_frames > 0 and (total_video_frames // step) > max_frames:
            step = max(1, total_video_frames // max_frames)

        temp_dir = tempfile.mkdtemp(prefix="argus_video_frames_")
        extracted = []
        frame_no = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_no % step == 0:
                timestamp = round(frame_no / fps, 2)
                frame_filename = os.path.join(temp_dir, f"frame_{frame_no:06d}.jpg")
                success = cv2.imwrite(frame_filename, frame)
                if success:
                    extracted.append({
                        "frame_no": frame_no,
                        "timestamp_sec": timestamp,
                        "path": frame_filename
                    })

                if len(extracted) >= max_frames:
                    break

            frame_no += 1

        cap.release()

        if not extracted:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise ValueError("No readable frames could be extracted from video.")

        logger.info(f"Extracted {len(extracted)} frames from {video_path} ({duration_sec}s @ {fps}fps)")

        return {
            "temp_dir": temp_dir,
            "fps": round(fps, 2),
            "total_video_frames": total_video_frames,
            "duration_sec": duration_sec,
            "frames": extracted
        }

    def cleanup(self, temp_dir: str):
        """Remove temporary frame directory."""
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"Error cleaning up temp directory {temp_dir}: {e}")


extractor = FrameExtractor()