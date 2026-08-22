import time
import torch
from typing import Dict, Any

from .model import get_model, get_processor, get_device
from .preprocess import load_image
from .forensics import image_forensics
from .face import detect_face
from utils.logger import logger


class ImageDetector:
    """
    Multimodal image verification combining Vision Transformers (ViT)
    with deterministic digital image forensics (Error Level Analysis & FFT).
    """

    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image for AI generation, manipulation, or deepfakes.
        """
        start_time = time.perf_counter()

        # Load and validate image
        image = load_image(image_path)

        # Run deterministic digital forensics
        forensic_signals = image_forensics.analyze(image)

        # Check for face presence
        face_crop = detect_face(image)
        face_detected = face_crop is not None

        processor = get_processor()
        model = get_model()
        device = get_device()

        # If Vision Transformer model is available
        if model is not None and processor is not None:
            try:
                # Preprocess for ViT
                # If face is detected, we prioritize evaluating the cropped face, or fallback to whole image
                target_img = face_crop if face_crop is not None else image
                inputs = processor(images=target_img, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = model(**inputs)
                    probabilities = torch.softmax(outputs.logits, dim=1)

                confidence, predicted = torch.max(probabilities, dim=1)
                idx = predicted.item()

                # Dynamic label resolution from model config
                if hasattr(model.config, "id2label") and idx in model.config.id2label:
                    raw_label = model.config.id2label[idx]
                else:
                    raw_label = "Real" if idx == 0 else "Fake"

                # Normalize label
                norm_label = "Fake" if str(raw_label).upper() in ("FAKE", "LABEL_1") else "Real"
                conf_val = round(confidence.item() * 100, 2)
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                return {
                    "media_type": "image",
                    "prediction": norm_label,
                    "confidence": conf_val,
                    "model": "Wvolf/ViT_Deepfake_Detection",
                    "device": str(device),
                    "face_detected": face_detected,
                    "forensics": forensic_signals,
                    "processing_time_ms": elapsed_ms
                }

            except Exception as e:
                logger.warning(f"Image ViT model inference failed ({e}). Falling back to forensic analyzer.")

        # Deterministic Forensic Fallback
        pred = forensic_signals.get("prediction", "Real")
        conf = forensic_signals.get("confidence", 65.0)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "media_type": "image",
            "prediction": pred,
            "confidence": conf,
            "model": "Deterministic Forensic Analyzer (ELA + Frequency Spectrum Fallback)",
            "device": "cpu",
            "face_detected": face_detected,
            "forensics": forensic_signals,
            "processing_time_ms": elapsed_ms
        }


# Singleton instance
detector = ImageDetector()


def detect_image(image_path: str) -> Dict[str, Any]:
    """Compatibility wrapper."""
    return detector.predict(image_path)
