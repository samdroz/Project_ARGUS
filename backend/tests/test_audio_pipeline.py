import io
import math
import struct
import wave
import tempfile
import os
import pytest

from ai.audio.features import load_wav_file, audio_features
from ai.audio.detector import detect_audio


def create_synthetic_wav_file(duration_sec: float = 1.0, freq: float = 440.0, sample_rate: int = 16000) -> str:
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_path = temp_file.name
    temp_file.close()

    total_samples = int(duration_sec * sample_rate)
    with wave.open(temp_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(total_samples):
            val = int(16000.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            wf.writeframes(struct.pack("<h", val))

    return temp_path


def test_audio_wav_loading_and_features():
    wav_path = create_synthetic_wav_file(duration_sec=1.0, freq=440.0)
    try:
        waveform, sr, duration = load_wav_file(wav_path)
        assert waveform.shape[0] == 1
        assert waveform.shape[1] == 16000
        assert sr == 16000
        assert round(duration, 1) == 1.0

        features = audio_features.extract_features(waveform, sr)
        assert "spectral_centroid_hz" in features
        assert "zero_crossing_rate" in features
        assert "spectral_flatness" in features
        assert features["sample_rate"] == 16000
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)


def test_audio_detector_inference():
    wav_path = create_synthetic_wav_file(duration_sec=1.0, freq=440.0)
    try:
        result = detect_audio(wav_path)
        assert result["media_type"] == "audio"
        assert result["prediction"] in ("Real", "Fake")
        assert result["confidence"] > 0
        assert "forensics" in result
        assert "model" in result
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
