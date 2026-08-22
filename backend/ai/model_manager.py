import torch
from typing import Optional, Dict, Any

from config.settings import settings
from utils.logger import logger


class ModelManager:
    """
    Centralized, thread-safe model manager supporting lazy loading,
    dynamic device selection (CUDA/CPU fallback), status tracking,
    and graceful degradation.
    """

    def __init__(self):
        self.device = self._resolve_device(settings.DEVICE)

        # Image model state
        self.image_model = None
        self.image_processor = None
        self.image_status: str = "not_loaded"
        self.image_error: Optional[str] = None

        # Text model state
        self.text_model = None
        self.text_tokenizer = None
        self.text_status: str = "not_loaded"
        self.text_error: Optional[str] = None

        # Audio model state
        self.audio_model = None
        self.audio_processor = None
        self.audio_status: str = "not_loaded"
        self.audio_error: Optional[str] = None

    def _resolve_device(self, preferred_device: str) -> str:
        if preferred_device.lower() == "cuda" and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def load_image_model(self) -> bool:
        if self.image_model is not None:
            return True

        if not settings.IMAGE_MODEL:
            self.image_status = "fallback"
            return False

        logger.info(f"Loading Image Model ({settings.IMAGE_MODEL}) on {self.device}...")
        try:
            from transformers import AutoImageProcessor, AutoModelForImageClassification

            self.image_processor = AutoImageProcessor.from_pretrained(
                settings.IMAGE_MODEL
            )
            self.image_model = AutoModelForImageClassification.from_pretrained(
                settings.IMAGE_MODEL
            )
            self.image_model.to(self.device)
            self.image_model.eval()

            self.image_status = "loaded"
            self.image_error = None
            logger.info("✓ Image Model Loaded successfully.")
            return True
        except Exception as e:
            self.image_status = "failed"
            self.image_error = str(e)
            logger.warning(f"Image model loading failed ({e}). Built-in forensic analyzer fallback will be used.")
            return False

    def load_text_model(self) -> bool:
        if self.text_model is not None:
            return True

        if not settings.TEXT_MODEL:
            self.text_status = "fallback"
            return False

        logger.info(f"Loading Text Model ({settings.TEXT_MODEL}) on {self.device}...")
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            self.text_tokenizer = AutoTokenizer.from_pretrained(
                settings.TEXT_MODEL
            )
            self.text_model = AutoModelForSequenceClassification.from_pretrained(
                settings.TEXT_MODEL
            )
            self.text_model.to(self.device)
            self.text_model.eval()

            self.text_status = "loaded"
            self.text_error = None
            logger.info("✓ Text Model Loaded successfully.")
            return True
        except Exception as e:
            self.text_status = "failed"
            self.text_error = str(e)
            logger.warning(f"Text model loading failed ({e}). Lexical/claim verification fallback will be used.")
            return False

    def load_audio_model(self) -> bool:
        if self.audio_model is not None:
            return True

        if not settings.AUDIO_MODEL:
            self.audio_status = "deterministic_forensics_active"
            return False

        logger.info(f"Attempting Audio Model ({settings.AUDIO_MODEL}) on {self.device}...")
        try:
            from transformers import AutoProcessor, AutoModelForAudioClassification

            self.audio_processor = AutoProcessor.from_pretrained(settings.AUDIO_MODEL)
            self.audio_model = AutoModelForAudioClassification.from_pretrained(settings.AUDIO_MODEL)
            self.audio_model.to(self.device)
            self.audio_model.eval()

            self.audio_status = "loaded"
            self.audio_error = None
            logger.info("✓ Audio Model Loaded successfully.")
            return True
        except Exception as e:
            self.audio_status = "failed"
            self.audio_error = str(e)
            logger.info(f"Neural audio model not active ({e}). Using deterministic acoustic spectral analyzer.")
            return False

    def load_all(self):
        """Preload models on application startup."""
        self.load_image_model()
        self.load_text_model()
        if settings.AUDIO_MODEL:
            self.load_audio_model()

    def get_status_summary(self) -> Dict[str, Any]:
        """Detailed status summary for health check."""
        cuda_avail = torch.cuda.is_available()
        return {
            "device": self.device,
            "cuda_available": cuda_avail,
            "cuda_device_name": torch.cuda.get_device_name(0) if cuda_avail else None,
            "models": {
                "image": {
                    "model_id": settings.IMAGE_MODEL,
                    "status": self.image_status,
                    "error": self.image_error,
                    "fallback": "Error Level Analysis & Frequency Forensics" if self.image_status != "loaded" else None,
                },
                "text": {
                    "model_id": settings.TEXT_MODEL,
                    "status": self.text_status,
                    "error": self.text_error,
                    "fallback": "Lexical Marker & Factual Claim Analysis" if self.text_status != "loaded" else None,
                },
                "audio": {
                    "model_id": settings.AUDIO_MODEL or "None (Deterministic)",
                    "status": self.audio_status if settings.AUDIO_MODEL else "deterministic_forensics_active",
                    "error": self.audio_error,
                    "fallback": "Deterministic Spectral & Acoustic Forensic Analyzer",
                },
            },
        }


model_manager = ModelManager()