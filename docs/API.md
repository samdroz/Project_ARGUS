# Project ARGUS — API Reference

All endpoints are served from `http://localhost:8000`. Interactive Swagger UI is available at `/docs`.

---

## Authentication

No authentication is required for local deployments. For production, configure `CORS_ORIGINS` and add an API key middleware.

---

## Common Response Schema

All analysis endpoints return a unified response object:

```json
{
  "status": "success",
  "analysis_id": "uuid-v4",
  "media_type": "text | image | video | audio | url",
  "verdict": "REAL | FAKE | SUSPICIOUS | UNVERIFIED | ...",
  "prediction": "Real | Fake | ...",
  "confidence": 0.87,
  "trust_score": 42,
  "risk_level": "LOW | MEDIUM | HIGH | CRITICAL | INSUFFICIENT_EVIDENCE",
  "model": "model-name",
  "file": { "id": "...", "name": "...", "saved_filename": "...", "path": "..." },
  "analysis": { /* raw detector output */ },
  "evidence": { /* fact-check results */ },
  "claims": [ /* per-claim verification */ ],
  "metadata": { /* file metadata / EXIF */ },
  "forensics": { /* digital forensics signals */ },
  "trust": {
    "score": 42,
    "risk": "HIGH",
    "verdict": "SUSPICIOUS",
    "recommendation": "...",
    "factors": [ "..." ],
    "limitations": [ "..." ]
  },
  "factors": [ "..." ],
  "recommendation": "...",
  "limitations": [ "..." ],
  "processing": {
    "time_ms": 312.5,
    "device": "cuda",
    "model": "hamzab/roberta-fake-news-classification"
  }
}
```

### Honest Uncertainty

When there is insufficient evidence to make a determination:

```json
{
  "trust_score": null,
  "risk_level": "INSUFFICIENT_EVIDENCE",
  "verdict": "UNVERIFIED"
}
```

`NO EVIDENCE ≠ FALSE`. Absence of corroborating sources does not mean content is fake.

---

## System Endpoints

### `GET /`

Returns application metadata.

**Response:**
```json
{
  "application": "Project ARGUS",
  "version": "2.0.0",
  "status": "Running",
  "supported_modalities": ["text", "image", "video", "audio", "url"],
  "docs_url": "/docs"
}
```

---

### `GET /health`

Returns live system and model health.

**Response:**
```json
{
  "status": "healthy",
  "application": { "name": "Project ARGUS", "version": "2.0.0" },
  "system": {
    "device": "cuda",
    "cuda_available": true,
    "cuda_device_name": "NVIDIA GeForce RTX 4060 Laptop GPU"
  },
  "models": {
    "image": { "model_id": "Wvolf/ViT_Deepfake_Detection", "status": "loaded", "error": null, "fallback": null },
    "text":  { "model_id": "hamzab/roberta-fake-news-classification", "status": "loaded", "error": null, "fallback": null },
    "audio": { "model_id": "acoustic-forensics-v1", "status": "loaded", "error": null, "fallback": null }
  },
  "services": {
    "trust_engine": "active",
    "metadata_analyzer": "active",
    "evidence_agent": "active",
    "forensics": "active",
    "report_service": "active"
  }
}
```

---

## Analysis Endpoints

### `POST /analyze/text`

Analyzes text for AI/misinformation markers and verifies extracted claims.

**Request Body (JSON):**
```json
{
  "title": "Headline or article title",
  "content": "Full article body text...",
  "verify_claims": true
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | Article headline |
| `content` | string | **Yes** | Article body (min 1 char after strip) |
| `verify_claims` | boolean | No | Enable claim extraction + fact-checking (default: true) |

**Error Responses:**
- `400` — Content is empty
- `500` — Internal model failure

---

### `POST /analyze/image`

Analyzes an uploaded image using ViT deepfake detection and deterministic ELA forensics.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Image file (JPG, JPEG, PNG, WebP, BMP) |

**Forensics fields returned:**
- `ela.max_diff` — Maximum ELA pixel difference (high = compression anomaly)
- `ela.mean_diff` — Mean ELA difference
- `ela.suspicious` — Boolean: ELA anomaly threshold exceeded
- `frequency_analysis.has_grid_pattern` — FFT grid pattern (indicates GAN generation)
- `frequency_analysis.spectral_energy_ratio` — High-frequency energy ratio
- `sharpness.laplacian_variance` — Image sharpness (blur detection)

**Error Responses:**
- `400` — Unsupported file extension, corrupt image
- `500` — Model failure

---

### `POST /analyze/video`

Analyzes a video clip by extracting frames and running per-frame deepfake detection with temporal aggregation.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Video file (MP4, AVI, MOV, MKV) |

**Analysis fields returned:**
- `frames_analyzed` — Number of frames sampled
- `suspicious_frames` — Count of frames flagged as fake
- `temporal_consistency` — Frame-to-frame confidence variance
- `suspicious_burst` — Boolean: consecutive suspicious frames detected

**Notes:**
- Frame sampling: every `VIDEO_FRAME_INTERVAL` frames (default: 30), capped at `VIDEO_MAX_FRAMES` (default: 10)
- Temp directories are always cleaned up in `finally` blocks

**Error Responses:**
- `400` — Unsupported extension, corrupt video
- `500` — OpenCV/extraction failure

---

### `POST /analyze/audio`

Analyzes an audio file for voice cloning, TTS artifacts, and spectral anomalies.

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | File | Audio file (WAV, MP3, OGG, FLAC) |

> **Note:** WAV files are loaded via Python's built-in `wave` module to avoid `torchcodec` dependency issues.

**Forensics fields returned:**
- `spectral_centroid_hz` — Mean spectral centroid in Hz
- `zero_crossing_rate` — Zero-crossing rate (TTS markers: abnormally regular)
- `spectral_flatness` — Noise-to-tone ratio (synthetic: low flatness)
- `pitch_stability` — Standard deviation of pitch (cloned voice: unnaturally stable)
- `spectral_discontinuity` — Frame boundary energy jumps
- `energy_variance` — Amplitude envelope regularity

**Error Responses:**
- `400` — Unsupported file type, corrupt audio
- `500` — Feature extraction failure

---

### `POST /analyze/url`

Fetches and analyzes a web URL — validates against SSRF, classifies domain credibility, extracts article content, and fact-checks claims.

**Request Body (JSON):**
```json
{
  "url": "https://example.com/article",
  "verify_claims": true
}
```

**SSRF Protection** — The following URL targets are blocked with `400`:
- Loopback addresses (`127.x.x.x`, `::1`, `localhost`)
- RFC 1918 private ranges (`10.x`, `172.16-31.x`, `192.168.x`)
- Link-local / multicast (`169.254.x.x`, `224.x`)
- AWS/GCP metadata (`169.254.169.254`)
- Non-HTTP(S) schemes (`file://`, `ftp://`, etc.)
- DNS rebinding (resolved IP must also pass all checks)

**Domain Quality Classes:**
- `VERY_HIGH` — Government (`.gov`), academic (`.edu`), AP, Reuters, BBC
- `HIGH` — Snopes, FactCheck.org, PolitiFact, Wikipedia
- `MEDIUM` — Known mainstream news outlets
- `LOW` — Unknown/unclassified domains

**Error Responses:**
- `400` — SSRF blocked, invalid URL scheme
- `500` — Fetch timeout, content extraction failure

---

## Claims Response Format

```json
{
  "claims": [
    {
      "claim_id": 1,
      "claim_text": "Scientists confirmed discovery of water on Mars",
      "verdict": "SUPPORTED | CONTRADICTED | MIXED | UNVERIFIED",
      "confidence": 0.75,
      "sources": [
        {
          "title": "NASA Confirms Water Ice on Mars",
          "url": "https://nasa.gov/...",
          "domain": "nasa.gov",
          "snippet": "...",
          "source_type": "government",
          "source_quality": "VERY_HIGH",
          "stance": "SUPPORTS"
        }
      ]
    }
  ]
}
```

---

## Trust Score Calculation

Trust score (0–100) is a weighted composite of:

| Signal | Weight | Description |
|--------|--------|-------------|
| Neural model confidence | 0.40 | Primary classifier output |
| Evidence direction | 0.25 | Supporting vs. contradicting sources |
| Source quality | 0.15 | Domain authority of evidence |
| Forensic anomalies | 0.15 | ELA / spectral / frequency signals |
| Stylistic markers | 0.05 | Clickbait, caps ratio, exclamation density |

A score of `null` is returned when `risk_level = INSUFFICIENT_EVIDENCE`.