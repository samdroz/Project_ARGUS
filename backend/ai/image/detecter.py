import time
import torch

from .model import model, processor, DEVICE
from .preprocess import load_image


class ImageDetector:
    def __init__(self):
        self.model = model
        self.processor = processor
        self.device = DEVICE

    @torch.no_grad()
    def predict(self, image_path: str):
        """
        Perform deepfake detection on an image.

        Args:
            image_path (str): Path to the uploaded image.

        Returns:
            dict: Prediction result.
        """

        start_time = time.perf_counter()

        # Load image
        image = load_image(image_path)

        # Preprocess
        inputs = self.processor(
            images=image,
            return_tensors="pt"
        )

        # Move tensors to GPU/CPU
        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        # Run inference
        outputs = self.model(**inputs)

        # Convert logits -> probabilities
        probabilities = torch.softmax(outputs.logits, dim=1)

        confidence, predicted = torch.max(probabilities, dim=1)

        label = self.model.config.id2label[predicted.item()]

        processing_time = (time.perf_counter() - start_time) * 1000

        return {
            "prediction": label,
            "confidence": round(confidence.item() * 100, 2),
            "model": "Wvolf/ViT_Deepfake_Detection",
            "device": str(self.device),
            "processing_time_ms": round(processing_time, 2)
        }


# Singleton instance
detector = ImageDetector()


def detect_image(image_path: str):
    """
    Compatibility wrapper for existing FastAPI code.
    """
    return detector.predict(image_path)