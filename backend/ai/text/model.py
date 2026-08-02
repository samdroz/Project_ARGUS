import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from config.settings import settings


MODEL_NAME = settings.TEXT_MODEL

DEVICE = (
    settings.DEVICE
    if torch.cuda.is_available()
    else "cpu"
)

print(f"Loading {MODEL_NAME}...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME
)

model.to(DEVICE)

model.eval()

print(f"Loaded on {DEVICE}")