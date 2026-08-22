from typing import Dict, Any
import os

from .exif import extract_exif
from .hash import generate_sha256


class MetadataAnalyzer:
    """
    Multimodal file metadata analyzer.
    Treats metadata anomalies (missing EXIF, editing tool tags) as weak/moderate signals,
    never as standalone proof of falsity.
    """

    def analyze(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {
                "file_hash": None,
                "file_size": 0,
                "metadata": {}
            }

        file_hash = generate_sha256(file_path)
        file_size = os.path.getsize(file_path)
        exif_info = extract_exif(file_path)

        # Classify metadata signal
        has_editing_tool = bool(exif_info.get("editing_software_detected"))
        missing_exif = not exif_info.get("has_exif", False)

        return {
            "file_hash": file_hash,
            "file_size_bytes": file_size,
            "has_exif": exif_info.get("has_exif", False),
            "editing_software": exif_info.get("editing_software_detected"),
            "camera_make": exif_info.get("camera_make"),
            "camera_model": exif_info.get("camera_model"),
            "dimensions": {
                "width": exif_info.get("width"),
                "height": exif_info.get("height")
            } if "width" in exif_info else None,
            "signal_note": (
                "File contains editing software signature."
                if has_editing_tool
                else ("Standard compressed/uploaded image (no camera EXIF)." if missing_exif else "Original camera metadata present.")
            )
        }


metadata_analyzer = MetadataAnalyzer()