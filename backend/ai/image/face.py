import cv2
import numpy as np
from PIL import Image


# Load OpenCV's built-in Haar Cascade
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def detect_face(image: Image.Image):
    """
    Detect the largest face in an image.

    Returns:
        PIL.Image if a face is found.
        None if no face is detected.
    """

    # Convert PIL Image -> OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = FACE_CASCADE.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(faces) == 0:
        return None

    # Select the largest detected face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

    face = image.crop((x, y, x + w, y + h))

    return face