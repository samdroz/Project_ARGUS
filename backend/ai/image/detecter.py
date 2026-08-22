# Backwards compatibility alias for detector.py
from .detector import ImageDetector, detector, detect_image

__all__ = ["ImageDetector", "detector", "detect_image"]