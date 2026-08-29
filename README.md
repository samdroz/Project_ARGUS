# Project ARGUS — Multimodal AI Verification Platform

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.11%2Bcu128-orange.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Project ARGUS** is a production-ready multimodal AI verification platform for detecting deepfakes, misinformation, and manipulated media. It combines neural AI models with deterministic digital forensics and an evidence-based fact-checking agent to produce calibrated, honest trust assessments.

---

## Features

| Modality | Detection Methods |
|----------|------------------|
| **Text** | RoBERTa fake-news classification · Stylistic/linguistic analysis · Claim extraction & fact-checking |
| **Image** | ViT deepfake detection · Error Level Analysis (ELA) · FFT frequency forensics · EXIF metadata |
| **Video** | Frame-level ViT detection · Temporal aggregation · Suspicious burst analysis |
| **Audio** | Spectral forensics (STFT, centroid, flatness) · Zero-crossing rate · Pitch stability · Spectral discontinuity |
| **URL** | SSRF-protected content extraction · Domain authority classification · Claim verification |

### Core Engine
- **Trust Engine** — Multi-signal calibrated trust scoring (0–100) with risk levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `INSUFFICIENT_EVIDENCE`
- **Fact-Checker Agent** — Modular search provider interface with DuckDuckGo and deterministic fallbacks
- **Honest Uncertainty** — No fabricated outputs. If evidence is insufficient: `trust_score = null`, `verdict = UNVERIFIED`
- **SSRF Protection** — Blocks loopback, private subnets, AWS/GCP metadata endpoints, non-HTTP schemes

---

## Architecture

```
PROJECT ARGUS/
├── backend/                    # FastAPI backend
│   ├── ai/
│   │   ├── model_manager.py    # Centralized lazy model loader (CUDA/CPU)
│   │   ├── text/               # RoBERTa text pipeline
│   │   ├── image/              # ViT + ELA image pipeline
│   │   ├── video/              # Frame extraction + temporal analysis
│   │   ├── audio/              # Spectral acoustic forensics
│   │   ├── url/                # SSRF validator + content extractor
│   │   ├── metadata/           # EXIF + file hash analysis
│   │   ├── fact_checker.py     # Claim verification agent
│   │   └── trust/              # Multi-signal trust engine
│   ├── api/                    # FastAPI route handlers
│   ├── services/               # Business logic layer
│   ├── schemas/                # Pydantic request/response models
│   ├── config/                 # Settings + constants/enums
│   ├── utils/                  # Logger, file handler
│   └── tests/                  # 35-test pytest suite
└── frontend/                   # Vanilla HTML/CSS/JS verification hub
    ├── index.html
    ├── styles.css
    └── app.js
```

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js v18+ (optional, only if rebuilding frontend)
- NVIDIA GPU recommended (CUDA 12.8+ for RTX 4060)

### 2. Install Dependencies

```powershell
cd "PROJECT ARGUS"
python -m venv venv
venv\Scripts\pip install -r backend\requirements.txt
```

### 3. Configure Environment

```powershell
# backend\.env is pre-configured with safe defaults
# Edit if needed:
notepad backend\.env
```

### 4. Start the Backend

```powershell
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Open the Verification Hub

Visit **http://localhost:8000/app** in your browser.

API documentation is at **http://localhost:8000/docs** (Swagger UI).

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Application info |
| `GET` | `/health` | Live health & model status |
| `POST` | `/analyze/text` | Analyze text / article |
| `POST` | `/analyze/image` | Analyze uploaded image |
| `POST` | `/analyze/video` | Analyze uploaded video |
| `POST` | `/analyze/audio` | Analyze uploaded audio |
| `POST` | `/analyze/url` | Analyze web URL |
| `GET` | `/app` | Frontend verification hub |

---

## Running Tests

```powershell
cd backend
..\venv\Scripts\python.exe -m pytest tests/ -v
```

**35 tests across 11 test modules — all passing.**

| Test Module | Coverage |
|-------------|---------|
| `test_api_endpoints.py` | All 5 modality endpoints + root + health |
| `test_text_pipeline.py` | Stylistic analyzer, claim extraction, RoBERTa detector |
| `test_image_pipeline.py` | ELA forensics, corrupt file handling, metadata |
| `test_audio_pipeline.py` | WAV loader, spectral features, acoustic detector |
| `test_trust_engine.py` | Trust scoring, risk levels, factor generation |
| `test_url_and_ssrf.py` | SSRF blocking, domain classification, deduplication |
| `test_fact_checker.py` | MockSearchProvider, stance evaluation, claim verification |
| `test_video.py` | Frame extraction, temp dir cleanup |
| `test_video_detector.py` | Temporal aggregation |
| `test_model.py` | ModelManager status reporting |
| `test_settings.py` | Configuration loading |

---

## Design Principles

1. **No fabricated outputs** — If a neural model fails to load, a deterministic fallback is used and honestly reported.
2. **Honest uncertainty** — `NO EVIDENCE ≠ FALSE`. Insufficient evidence yields `trust_score = null`, `risk = INSUFFICIENT_EVIDENCE`.
3. **SSRF security** — All external URL fetches pass through strict IP/hostname validation.
4. **Calibrated trust** — Trust score is a multi-signal weighted composite, not a simple confidence inversion.
5. **Lazy model loading** — Models load on first use or at startup, with CUDA/CPU fallback.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Project ARGUS` | Application name |
| `APP_VERSION` | `2.0.0` | Version string |
| `DEBUG` | `false` | Debug mode |
| `PORT` | `8000` | Server port |
| `DEVICE` | `auto` | `cuda`, `cpu`, or `auto` |
| `MAX_UPLOAD_SIZE` | `52428800` | Max file size (50MB) |
| `TEXT_MODEL_ID` | `hamzab/roberta-fake-news-classification` | HuggingFace model |
| `IMAGE_MODEL_ID` | `Wvolf/ViT_Deepfake_Detection` | HuggingFace model |
| `VIDEO_FRAME_INTERVAL` | `30` | Frames between samples |
| `VIDEO_MAX_FRAMES` | `10` | Max frames per video |
| `SEARCH_PROVIDER` | `duckduckgo` | `duckduckgo` or `mock` |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

---

## License

MIT License — see [LICENSE](LICENSE).

---

> **Disclaimer**: Results are probabilistic assessments based on AI models and deterministic forensics. They are not definitive truth determinations. Always apply critical thinking and consult primary sources.
