# Project ARGUS — System Architecture

## Overview

Project ARGUS is a layered multimodal verification platform. Each modality follows the same pipeline pattern: **input validation → AI inference → forensics → trust synthesis → standardized response**.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Frontend (Vanilla JS)                          │
│  Text │ Image │ Video │ Audio │ URL   ←→   Trust Meter │ Claim Cards │
└────────────────────────────┬─────────────────────────────────────────┘
                             │  HTTP (REST / multipart)
┌────────────────────────────▼─────────────────────────────────────────┐
│                        FastAPI Backend                                │
│                                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ /text    │ │ /image   │ │ /video   │ │ /audio   │ │ /url     │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │             │             │             │             │        │
│  ┌────▼─────────────▼─────────────▼─────────────▼─────────────▼───┐  │
│  │                       Service Layer                              │  │
│  │  text_service  image_service  video_service  audio_service      │  │
│  │  url_service   report_service                                    │  │
│  └──────────────────────────┬───────────────────────────────────────┘  │
│                             │                                          │
│  ┌──────────────────────────▼───────────────────────────────────────┐  │
│  │                         AI Layer                                  │  │
│  │                                                                   │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐              │  │
│  │  │ ModelManager│  │ FactChecker │  │  Trust Engine│              │  │
│  │  │ (lazy CUDA)│  │ (search+NLI)│  │  (scoring)   │              │  │
│  │  └────────────┘  └─────────────┘  └──────────────┘              │  │
│  │                                                                   │  │
│  │  text/  image/  video/  audio/  url/  metadata/                 │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Layer Descriptions

### 1. API Layer (`api/`)

FastAPI routers with input validation and error handling. Each router delegates to its service immediately — no business logic here.

- `api/text.py` → validates `TextRequest` (title, content, verify_claims)
- `api/image.py` → validates file extension, delegates to `image_service`
- `api/video.py` → validates file extension, delegates to `video_service`
- `api/audio.py` → validates file extension, delegates to `audio_service`
- `api/url.py` → validates `URLRequest`, delegates to `url_service`

### 2. Service Layer (`services/`)

Orchestrates the full pipeline for each modality:

1. **Preprocessing** — format validation, corruption detection, normalization
2. **AI Inference** — neural model prediction (with deterministic fallback on load failure)
3. **Forensics/Analysis** — modality-specific deterministic analysis
4. **Trust Calculation** — multi-signal scoring via `trust/engine.py`
5. **Report Assembly** — standardized response via `report_service.build_report()`

### 3. AI Layer (`ai/`)

#### ModelManager (`ai/model_manager.py`)
- Centralized lazy model loading with thread-safe initialization
- CUDA detection with automatic CPU fallback
- Per-model status tracking: `loaded`, `failed`, `fallback`
- Dynamic `id2label` resolution to avoid label inversion bugs

#### Text Pipeline (`ai/text/`)
- `preprocess.py` — whitespace normalization, length truncation
- `analyzer.py` — stylistic markers (clickbait patterns, caps ratio, exclamation count, atomic claim extraction)
- `detector.py` — RoBERTa (`hamzab/roberta-fake-news-classification`) with dynamic label normalization

#### Image Pipeline (`ai/image/`)
- `preprocess.py` — EXIF orientation correction, corruption detection
- `forensics.py` — Error Level Analysis (ELA), 2D FFT grid detection, Laplacian sharpness
- `face.py` — OpenCV 5.x-compatible face detector with `hasattr` safety guard
- `detector.py` — ViT (`Wvolf/ViT_Deepfake_Detection`) with fallback to forensics-only

#### Video Pipeline (`ai/video/`)
- `extractor.py` — Per-request isolated temp dirs (`tempfile.mkdtemp`), FPS validation, interval sampling, guaranteed cleanup in `finally`
- `detector.py` — Per-frame ViT inference
- `analyzer.py` — Temporal aggregation, suspicious burst detection, consistency variance

#### Audio Pipeline (`ai/audio/`)
- `features.py` — Python `wave` + `torch.frombuffer` WAV loader (avoids `torchcodec` dependency); STFT spectrogram, spectral centroid, flatness, ZCR, pitch stability, spectral discontinuity
- `detector.py` — Deterministic acoustic forensic scoring

#### URL Pipeline (`ai/url/`)
- `validator.py` — SSRF protection: blocks loopback, RFC 1918, link-local, metadata endpoints, non-HTTP schemes; DNS rebinding prevention via socket resolution
- `extractor.py` — `httpx` content fetch with 8s timeout and 5MB size limit
- `classifier.py` — Domain authority classification

#### Fact-Checker (`ai/fact_checker.py`)
- `SearchProvider` abstract interface
- `DuckDuckGoSearchProvider` — live web search
- `MockSearchProvider` — deterministic testing provider
- Source deduplication (syndicated wire service dedup)
- Stance evaluation: `SUPPORTS`, `CONTRADICTS`, `NEUTRAL`, `UNVERIFIED`
- Domain categorization: Government, Academic, Fact-Checker, Reputable News, Encyclopedia, Secondary, Unknown

#### Trust Engine (`ai/trust/`)
- `engine.py` — Weighted multi-signal composite scoring
- `risk.py` — Risk level mapping with `INSUFFICIENT_EVIDENCE` guard
- `explain.py` — Human-readable factor generation
- `recommendation.py` — Context-aware guidance based on risk + prediction

#### Metadata (`ai/metadata/`)
- `exif.py` — EXIF tag parsing, editing software signature detection (Adobe, GIMP, etc.)
- `hash.py` — SHA-256 file fingerprinting
- `analyzer.py` — Calibrated metadata anomaly signals

### 4. Configuration (`config/`)

- `settings.py` — Pydantic-validated settings from environment / `.env`
- `constants.py` — Enums: `RiskLevel`, `ClaimVerdict`, `EvidenceDirection`, `SourceCategory`

### 5. Schemas (`schemas/`)

- `response.py` — `StandardResponse` Pydantic model (unified across all modalities)
- `text.py` — `TextRequest`
- `url.py` — `URLRequest`

---

## Data Flow — Text Verification

```
POST /analyze/text (JSON)
    │
    ▼
api/text.py → validates TextRequest
    │
    ▼
services/text_service.py
    ├── ai/text/preprocess.py   (normalize)
    ├── ai/text/detector.py     (RoBERTa inference)
    ├── ai/text/analyzer.py     (stylistic markers, claim extraction)
    ├── ai/fact_checker.py      (claim verification via search)
    ├── ai/trust/engine.py      (multi-signal scoring)
    └── services/report_service.py (assemble StandardResponse)
    │
    ▼
JSON response
```

---

## Security Architecture

### SSRF Defense (URL Modality)

```python
# ai/url/validator.py — checks performed in order:
1. Scheme whitelist: only https:// and http://
2. Hostname blocklist: localhost, 127.x, ::1
3. ipaddress.ip_address(hostname).is_private → block RFC 1918
4. ipaddress.ip_address(hostname).is_loopback → block
5. ipaddress.ip_address(hostname).is_link_local → block (169.254.x)
6. ipaddress.ip_address(hostname).is_multicast → block
7. socket.getaddrinfo(hostname) → DNS resolve → re-check resolved IP
   (prevents DNS rebinding attacks)
```

### File Upload Security

- Extension whitelist per modality (no `.exe`, `.sh`, etc.)
- Size limit enforced at handler level (`MAX_UPLOAD_SIZE`)
- Files saved to isolated temp paths with UUID-based filenames
- Original filename preserved in metadata only (not used for path operations)

---

## Deterministic Fallbacks

When a neural model fails to load (network, CUDA OOM, etc.), the system degrades gracefully:

| Modality | Fallback |
|----------|---------|
| Text | Linguistic analysis only (stylistic markers, claim extraction) |
| Image | ELA + FFT forensics only (no ViT classification) |
| Video | Frame-level forensics only |
| Audio | Acoustic spectral forensics only |

Fallback usage is always honestly reported in the `model` field of the response and in `limitations`.

---

## Known Quirks

| Issue | Resolution |
|-------|-----------|
| `cv2.CascadeClassifier` missing in OpenCV 5.0.0 | `hasattr(cv2, 'CascadeClassifier')` guard in `face.py` |
| `torchaudio.load()` requires `torchcodec` in PyTorch 2.11+ | Use Python `wave` + `torch.frombuffer` in `features.py` |
| ViT `id2label` returns `{0: 'Real', 1: 'Fake'}` | Dynamic `id2label` normalization in `detector.py` |
| RoBERTa `id2label` returns `{0: 'FAKE', 1: 'TRUE'}` | Normalized to canonical `Real`/`Fake` strings |
| `report_service.build_report()` called with both `metadata` and `metadata_result` kwarg names | Both accepted via union parameter handling |