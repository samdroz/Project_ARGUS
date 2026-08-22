import os
from ai.image.preprocess import load_image
from ai.image.face import detect_face


def test_face_detection():
    sample_path = os.path.join(os.path.dirname(__file__), "test.jpg")
    if os.path.exists(sample_path):
        img = load_image(sample_path)
        assert img.width > 0
        assert img.height > 0
        # Face detect may return PIL image or None
        face = detect_face(img)
        assert face is None or face.width > 0