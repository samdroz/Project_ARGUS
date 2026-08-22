from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from typing import Dict, Any
import os


def extract_exif(file_path: str) -> Dict[str, Any]:
    """
    Extract and safely serialize EXIF and image header metadata.
    Detects editing software signatures and camera metadata.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found."}

    metadata: Dict[str, Any] = {
        "file_size_bytes": os.path.getsize(file_path),
        "editing_software_detected": None,
        "camera_make": None,
        "camera_model": None,
        "has_exif": False
    }

    try:
        image = Image.open(file_path)
        metadata["width"] = image.width
        metadata["height"] = image.height
        metadata["format"] = image.format

        raw_exif = image.getexif()
        if raw_exif:
            metadata["has_exif"] = True
            raw_tags = {}
            for tag_id, val in raw_exif.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                # Safely serialize bytes/complex objects
                if isinstance(val, (bytes, bytearray)):
                    try:
                        val_str = val.decode("utf-8", errors="ignore").strip()
                    except Exception:
                        val_str = f"<bytes len={len(val)}>"
                else:
                    val_str = str(val)

                raw_tags[tag_name] = val_str

            metadata["tags"] = raw_tags

            # Extract software & camera tags
            software = raw_tags.get("Software", "")
            make = raw_tags.get("Make", "")
            model = raw_tags.get("Model", "")

            if software:
                metadata["editing_software_detected"] = software
            if make:
                metadata["camera_make"] = make
            if model:
                metadata["camera_model"] = model

    except Exception as e:
        metadata["parsing_error"] = str(e)

    return metadata