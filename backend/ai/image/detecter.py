from pathlib import Path
import random


def detect_image(image_path: str) -> tuple[str, float]:
    """
    Simulates image analysis.

    Later this function will load a real AI model
    and return the prediction and confidence.
    """

    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    prediction = random.choice(["Real", "Fake"])
    confidence = round(random.uniform(70, 99), 2)

    return prediction, confidence