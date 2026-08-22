import time
import torch
from typing import Dict, Any

from .features import load_wav_file, audio_features
from ai.model_manager import model_manager
from utils.logger import logger


class AudioDetector:
    """
    Audio verification detector combining acoustic feature forensics
    with neural model inference (with transparent deterministic fallback).
    """

    def predict(self, audio_path: str) -> Dict[str, Any]:
        start_time = time.perf_counter()

        # Load audio waveform
        waveform, sample_rate, duration_sec = load_wav_file(audio_path)

        # Extract deterministic acoustic features
        features = audio_features.extract_features(waveform, sample_rate)

        # Check for neural audio model
        if model_manager.audio_model is not None and model_manager.audio_processor is not None:
            try:
                processor = model_manager.audio_processor
                model = model_manager.audio_model
                device = model_manager.device

                inputs = processor(
                    waveform.squeeze().numpy(),
                    sampling_rate=sample_rate,
                    return_tensors="pt"
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}

                with torch.no_grad():
                    outputs = model(**inputs)
                    probs = torch.softmax(outputs.logits, dim=-1)[0]

                conf, pred_idx = torch.max(probs, dim=-1)
                idx_int = pred_idx.item()
                raw_label = model.config.id2label.get(idx_int, "Real") if hasattr(model.config, "id2label") else ("Real" if idx_int == 0 else "Fake")
                norm_label = "Fake" if str(raw_label).upper() in ("FAKE", "SYNTHETIC", "SPOOF") else "Real"

                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {
                    "media_type": "audio",
                    "prediction": norm_label,
                    "confidence": round(conf.item() * 100, 2),
                    "duration_sec": round(duration_sec, 2),
                    "model": settings.AUDIO_MODEL,
                    "device": str(device),
                    "forensics": features,
                    "processing_time_ms": elapsed_ms
                }
            except Exception as e:
                logger.warning(f"Neural audio model inference error ({e}). Using deterministic acoustic fallback.")

        # Deterministic Acoustic Forensics Evaluation
        has_disc = features.get("spectral_discontinuity", False)
        unnatural_pitch = features.get("unnatural_pitch_stability", False)
        zcr = features.get("zero_crossing_rate", 0.0)

        anomaly_count = sum([has_disc, unnatural_pitch, zcr > 0.35])

        if anomaly_count >= 2:
            prediction = "Fake"
            confidence = 82.5
        elif anomaly_count == 1:
            prediction = "Fake"
            confidence = 68.0
        else:
            prediction = "Real"
            confidence = 74.0

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "media_type": "audio",
            "prediction": prediction,
            "confidence": confidence,
            "duration_sec": round(duration_sec, 2),
            "model": "Deterministic Acoustic & Spectral Forensic Analyzer (Fallback)",
            "device": "cpu",
            "forensics": features,
            "processing_time_ms": elapsed_ms
        }


audio_detector = AudioDetector()


def detect_audio(audio_path: str) -> Dict[str, Any]:
    return audio_detector.predict(audio_path)
