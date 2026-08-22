import torch
import time
from typing import Dict, Any

from .model import get_model, get_tokenizer, get_device
from .preprocess import prepare_text
from .analyzer import text_analyzer
from utils.logger import logger


def normalize_label(raw_label: str) -> str:
    """
    Normalize model output label to standard 'Fake' or 'Real'.
    """
    raw_upper = str(raw_label).upper().strip()
    if raw_upper in ("FAKE", "LABEL_0", "MISINFORMATION", "FALSE"):
        return "Fake"
    elif raw_upper in ("TRUE", "REAL", "LABEL_1", "CREDIBLE"):
        return "Real"
    return raw_label.capitalize()


def detect_text(title: str, content: str) -> Dict[str, Any]:
    """
    Detect potential misinformation/stylistic fake news in text.
    Distinguishes model stylistic classification from external factual verification.
    """
    start_time = time.perf_counter()
    full_text = prepare_text(title, content)

    if not full_text:
        return {
            "media_type": "text",
            "prediction": "Unverified",
            "confidence": 0.0,
            "model": "None",
            "device": "cpu",
            "stylistic_signals": {},
            "processing_time_ms": 0.0
        }

    # Extract stylistic features
    style_signals = text_analyzer.analyze_style(full_text)

    tokenizer = get_tokenizer()
    model = get_model()
    device = get_device()

    # If RoBERTa neural model is available
    if model is not None and tokenizer is not None:
        try:
            inputs = tokenizer(
                full_text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors="pt"
            )

            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1)[0]

            confidence, index = torch.max(probs, dim=0)
            idx_int = index.item()

            # Retrieve label dynamically from model config id2label
            if hasattr(model.config, "id2label") and idx_int in model.config.id2label:
                raw_label = model.config.id2label[idx_int]
            else:
                raw_label = "Fake" if idx_int == 0 else "Real"

            norm_label = normalize_label(raw_label)
            conf_val = round(confidence.item() * 100, 2)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            return {
                "media_type": "text",
                "prediction": norm_label,
                "confidence": conf_val,
                "model": "hamzab/roberta-fake-news-classification",
                "device": str(device),
                "stylistic_signals": style_signals,
                "processing_time_ms": elapsed_ms,
                "raw_label": str(raw_label)
            }

        except Exception as e:
            logger.warning(f"RoBERTa text inference error ({e}). Falling back to stylistic analyzer.")

    # Deterministic fallback analyzer
    sensationalism = style_signals.get("sensationalism_score", 0)
    if sensationalism >= 60:
        pred = "Fake"
        conf = round(50 + (sensationalism / 2.5), 2)
    elif sensationalism <= 20:
        pred = "Real"
        conf = round(70 - (sensationalism / 2), 2)
    else:
        pred = "Unverified"
        conf = 50.0

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return {
        "media_type": "text",
        "prediction": pred,
        "confidence": conf,
        "model": "Deterministic Stylistic & Lexical Analyzer (Fallback)",
        "device": "cpu",
        "stylistic_signals": style_signals,
        "processing_time_ms": elapsed_ms
    }