# CHANGELOG

All notable changes to Project ARGUS are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] — 2026-08-22

### Phase 1 — Foundation

**Fixed**
- `requirements.txt` was corrupted UTF-16; rewrote as clean UTF-8 for both root and `backend/` copies
- `config/settings.py` replaced brittle `os.environ` direct access with Pydantic `BaseSettings` with typed fields and safe defaults
- `config/constants.py` added enums: `RiskLevel`, `ClaimVerdict`, `EvidenceDirection`, `SourceCategory`
- `ai/model_manager.py` fully refactored: centralized lazy loading, CUDA/CPU fallback, per-model status tracking, dynamic `id2label` resolution
- `schemas/response.py` introduced `StandardResponse` unified schema across all modalities
- `main.py` lifespan startup, dynamic `/health` endpoint with real model status, CORS middleware

### Phase 2 — Modalities

**Text Pipeline** (`ai/text/`)
- `preprocess.py` — whitespace normalization, length truncation
- `analyzer.py` — clickbait detection, caps ratio, exclamation count, atomic claim extraction
- `detector.py` — RoBERTa inference with dynamic `id2label` normalization and deterministic fallback

**Image Pipeline** (`ai/image/`)
- `preprocess.py` — EXIF orientation correction, corruption validation
- `forensics.py` — Error Level Analysis (ELA), 2D FFT grid pattern detection, Laplacian sharpness
- `face.py` — OpenCV 5.0.0-compatible face detector with `hasattr` guard
- `detector.py` / `detecter.py` — ViT deepfake detection with backwards-compatibility alias

**Video Pipeline** (`ai/video/`)
- `extractor.py` — Isolated per-request temp dirs, FPS validation fallback, interval sampling, guaranteed cleanup
- `detector.py` — Per-frame ViT inference
- `analyzer.py` — Temporal aggregation, suspicious burst detection

**Fixed**
- `video_service.py` — `report_service.build_report()` keyword argument bug resolved

### Phase 3 — Trust Engine

**Added** (`ai/trust/`)
- `engine.py` — Multi-signal weighted trust scoring replacing simplistic `100 - confidence`
- `risk.py` — Risk level mapping including `INSUFFICIENT_EVIDENCE` with nullable `trust_score`
- `explain.py` — Evidence-backed human-readable factor generation
- `recommendation.py` — Context-aware guidance per risk + prediction combination

### Phase 4 — Evidence & URL

**Added** (`ai/fact_checker.py`)
- `SearchProvider` abstract interface
- `DuckDuckGoSearchProvider` — live web search
- `MockSearchProvider` — deterministic test provider
- Domain authority classification (7 tiers)
- Syndicated source deduplication
- Claim stance evaluation: `SUPPORTS`, `CONTRADICTS`, `NEUTRAL`, `UNVERIFIED`

**Added** (`ai/url/`)
- `validator.py` — SSRF protection: loopback, RFC 1918, link-local, metadata endpoints, DNS rebinding prevention
- `extractor.py` — `httpx` content fetcher (8s timeout, 5MB limit)
- `classifier.py` — Domain quality classification
- `services/url_service.py` — Orchestration

### Phase 5 — Audio

**Added** (`ai/audio/`)
- `features.py` — Python `wave` + `torch.frombuffer` WAV loader (bypasses `torchcodec` requirement); STFT, spectral centroid, flatness, ZCR, pitch stability, spectral discontinuity
- `detector.py` — Deterministic acoustic forensic scoring
- `services/audio_service.py` — Full pipeline orchestration
- `api/audio.py` — Audio analysis endpoint

### Phase 6 — Test Suite

**Added** (35 tests, all passing)
- `tests/test_api_endpoints.py` — Integration tests for all 5 modality endpoints + root + health
- `tests/test_text_pipeline.py` — Stylistic analyzer, claim extraction, RoBERTa detector
- `tests/test_image_pipeline.py` — ELA forensics, corrupt file rejection, metadata extraction
- `tests/test_audio_pipeline.py` — Synthetic WAV fixture, spectral features, acoustic detector
- `tests/test_trust_engine.py` — Trust scoring, risk levels, insufficient evidence
- `tests/test_url_and_ssrf.py` — SSRF blocking (localhost, private IPs, non-HTTP), domain classification, deduplication
- `tests/test_fact_checker.py` — MockSearchProvider, stance evaluation, claim verification
- `tests/test_video.py` — Frame extraction and temp dir cleanup
- `tests/test_video_detector.py` — Temporal aggregation on test.mp4
- `tests/test_model.py` — ModelManager status reporting
- `tests/test_settings.py` — Configuration validation
- Fixed legacy `test_detector.py`, `test_face.py`, `test_video.py`, `test_video_detector.py`, `test_model.py`, `test_settings.py`, `test_text.py`, `gpu_test.py` from module-level execution to proper `pytest` functions

**Fixed**
- `services/report_service.py` — `build_report()` now accepts both `metadata` and `metadata_result` keyword argument names for backward compatibility

### Phase 7 — Frontend

**Added** (`frontend/`)
- `index.html` — Complete verification hub with 5 modality panels, trust meter ring, results cards, claim breakdown, forensics display, history
- `styles.css` — Premium dark-mode UI with glassmorphism, CSS custom properties, trust ring SVG animation, responsive layout, Google Fonts (Inter + JetBrains Mono)
- `app.js` — Vanilla JS API client: drag-and-drop file upload, real-time analysis, animated trust ring, claim cards with source quality badges, localStorage history, live backend health polling

**Modified**
- `backend/main.py` — Added `StaticFiles` mount at `/static` and `FileResponse` at `/app` to serve frontend directly from the backend

### Phase 8 — Documentation

**Updated**
- `README.md` — Complete rewrite reflecting verified capabilities, architecture overview, quick start, API table, test summary, design principles
- `docs/API.md` — Full API reference: all endpoints, request/response schemas, forensics fields, SSRF rules, trust scoring formula
- `docs/ARCHITECTURE.md` — System diagram, layer descriptions, data flow, security architecture, known quirks
- `CHANGELOG.md` — This file

---

## [1.0.0] — Initial Repository

- Partial skeleton: basic FastAPI setup, placeholder routes
- Incomplete model loading (no fallbacks, no health reporting)
- No trust engine, no fact-checker, no audio pipeline
- Requirements file corrupted (UTF-16 encoding)
- Tests failed at collection due to module-level file path errors