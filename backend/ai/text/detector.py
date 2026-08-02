import torch

from .model import (
    tokenizer,
    model,
    DEVICE
)

from .preprocess import prepare_text


LABELS = [
    "Fake",
    "Real"
]


def detect_text(
    title: str,
    content: str
):

    text = prepare_text(
        title,
        content
    )

    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )

    inputs = {
        k: v.to(DEVICE)
        for k, v in inputs.items()
    }

    with torch.no_grad():

        outputs = model(**inputs)

        probs = torch.softmax(
            outputs.logits,
            dim=1
        )[0]

    confidence, index = torch.max(
        probs,
        dim=0
    )

    return {
        "media_type": "text",
        "prediction": LABELS[index.item()],
        "confidence": round(
            confidence.item() * 100,
            2
        ),
        "model": "RoBERTa Fake News",
        "device": DEVICE
    }