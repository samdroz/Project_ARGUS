import numpy as np
from PIL import Image
from typing import Optional


def detect_face(image: Image.Image) -> Optional[Image.Image]:
    """
    Detect and crop the primary face in an image if a face detector is available.
    Returns the cropped PIL face image or None (which falls back to the full image).
    """
    try:
        import cv2

        # Check for CascadeClassifier if available in OpenCV build
        if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if not face_cascade.empty():
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(60, 60)
                )
                if len(faces) > 0:
                    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                    # Add 10% padding
                    pad_x = int(w * 0.1)
                    pad_y = int(h * 0.1)
                    x1 = max(0, x - pad_x)
                    y1 = max(0, y - pad_y)
                    x2 = min(image.width, x + w + pad_x)
                    y2 = min(image.height, y + h + pad_y)
                    return image.crop((x1, y1, x2, y2))

    except Exception:
        pass

    return None