import torch

from transformers import (
    AutoImageProcessor,
    AutoModelForImageClassification
)

from config.settings import settings


MODEL_NAME = settings.IMAGE_MODEL

DEVICE = (
    settings.DEVICE
    if torch.cuda.is_available()
    else "cpu"
)

print(f"Loading {MODEL_NAME}...")

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

model = AutoModelForImageClassification.from_pretrained(
    MODEL_NAME
)

model.to(DEVICE)

model.eval()

print(f"Loaded on {DEVICE}")