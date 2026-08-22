from PIL import Image, ImageOps
from typing import Optional
import os


def load_image(image_path: str, max_dimension: int = 4096) -> Image.Image:
    """
    Safely load, validate, and preprocess an image for deepfake and forensic detection.
    Normalizes EXIF orientation and converts to RGB.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Check file size (prevent decompression bomb / corrupt zero-byte files)
    file_size = os.path.getsize(image_path)
    if file_size == 0:
        raise ValueError("Image file is empty (0 bytes).")

    try:
        image = Image.open(image_path)
        image.verify()  # Fast check for corruption
    except Exception as e:
        raise ValueError(f"Corrupted or invalid image file: {e}")

    # Re-open after verify() closes the file descriptor
    image = Image.open(image_path)

    # Correct EXIF rotation if present
    try:
        image = ImageOps.exif_transpose(image)
    except Exception:
        pass

    # Ensure RGB
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize if extremely large to prevent OOM
    if max(image.width, image.height) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    return image