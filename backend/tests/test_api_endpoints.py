import io
import math
import struct
import wave
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import numpy as np

from main import app

client = TestClient(app)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Running"
    assert "supported_modalities" in data


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "models" in data
    assert "services" in data


def test_text_analysis_api():
    payload = {
        "title": "NASA Mars Discovery",
        "content": "NASA scientists confirmed the detection of organic molecules on the Martian surface.",
        "verify_claims": False
    }
    resp = client.post("/analyze/text", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["media_type"] == "text"
    assert "trust" in data
    assert "factors" in data


def test_text_analysis_empty_content():
    resp = client.post("/analyze/text", json={"title": "Empty", "content": "   "})
    assert resp.status_code == 400


def test_image_analysis_api():
    # In-memory JPEG
    img_arr = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(img_arr).save(buf, format="JPEG")
    buf.seek(0)

    resp = client.post(
        "/analyze/image",
        files={"file": ("test_upload.jpg", buf, "image/jpeg")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["media_type"] == "image"
    assert "trust_score" in data
    assert "forensics" in data


def test_audio_analysis_api():
    # In-memory WAV
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        for i in range(8000):  # 0.5s
            val = int(16000.0 * math.sin(2.0 * math.pi * 440.0 * i / 16000))
            wf.writeframes(struct.pack("<h", val))
    buf.seek(0)

    resp = client.post(
        "/analyze/audio",
        files={"file": ("test_speech.wav", buf, "audio/wav")}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["media_type"] == "audio"
    assert "trust_score" in data


def test_url_ssrf_blocking_api():
    resp = client.post(
        "/analyze/url",
        json={"url": "http://127.0.0.1:8000/internal"}
    )
    assert resp.status_code == 400
    assert "SSRF" in resp.json()["detail"] or "forbidden" in resp.json()["detail"].lower()
