import torch

from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification,
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from config.settings import settings
from utils.logger import logger


class ModelManager:

    def __init__(self):

        self.device = (
            settings.DEVICE
            if torch.cuda.is_available()
            else "cpu"
        )

        self.image_model = None
        self.image_processor = None

        self.text_model = None
        self.text_tokenizer = None

    def load_image_model(self):

        logger.info("Loading Image Model...")

        self.image_processor = AutoImageProcessor.from_pretrained(
            settings.IMAGE_MODEL
        )

        self.image_model = AutoModelForImageClassification.from_pretrained(
            settings.IMAGE_MODEL
        )

        self.image_model.to(self.device)

        self.image_model.eval()

        logger.info("✓ Image Model Loaded")

    def load_text_model(self):

        logger.info("Loading Text Model...")

        self.text_tokenizer = AutoTokenizer.from_pretrained(
            settings.TEXT_MODEL
        )

        self.text_model = AutoModelForSequenceClassification.from_pretrained(
            settings.TEXT_MODEL
        )

        self.text_model.to(self.device)

        self.text_model.eval()

        logger.info("✓ Text Model Loaded")

    def load_all(self):

        self.load_image_model()
        self.load_text_model()


model_manager = ModelManager()