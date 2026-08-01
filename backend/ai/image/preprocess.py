from PIL import Image


def load_image(image_path: str):
    """
    Load an image for deepfake detection.
    Face detection will be added in a future version.
    """

    return Image.open(image_path).convert("RGB")