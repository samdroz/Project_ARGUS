# Project ARGUS API Documentation

This document describes every public endpoint exposed by the Project ARGUS backend.

| | |
|---|---|
| **Base URL** | `http://localhost:8000` |
| **Interactive Docs (Swagger)** | `http://localhost:8000/docs` |
| **Current Version** | `1.1.0` |

All endpoints return JSON. File upload endpoints accept `multipart/form-data`; all other endpoints accept and return `application/json`.

## Table of Contents

- [Response Format](#response-format)
- [Error Format](#error-format)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Image Analysis](#image-analysis)
  - [Video Analysis](#video-analysis)
  - [Text Analysis](#text-analysis)
  - [Health Check](#health-check)
  - [Root Endpoint](#root-endpoint)
- [HTTP Status Codes](#http-status-codes)
- [Versioning](#versioning)

---

## Response Format

Every successful API response follows a standardized format:

```json
{
  "status": "success",
  "file": {
    "id": "...",
    "name": "example.jpg"
  },
  "analysis": {
    "...": "..."
  }
}
```

## Error Format

Errors are returned in a consistent structure:

```json
{
  "status": "error",
  "message": "Unsupported file type."
}
```

## Authentication

The API does not currently require authentication. Support for API key and user-based authentication is planned for a future release — see the [Roadmap](README.md#roadmap).

---

## Endpoints

### Image Analysis

`POST /analyze/image`

Analyzes an uploaded image for signs of manipulation or AI generation.

**Request** — `multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | image file | Yes | Accepted formats: `jpg`, `jpeg`, `png`, `webp` |

Maximum upload size: 50 MB (configurable via `MAX_UPLOAD_SIZE`).

**Response** — `200 OK`

```json
{
  "status": "success",
  "file": {
    "id": "...",
    "name": "image.jpg"
  },
  "analysis": {
    "prediction": "Real",
    "confidence": 94.23,
    "trust_score": 94,
    "risk_level": "LOW",
    "recommendation": "...",
    "factors": []
  }
}
```

**Error Responses**

| Code | Cause |
|---|---|
| `400` | Unsupported file type |
| `400` | File exceeds the maximum upload size |
| `500` | Internal server error |

---

### Video Analysis

`POST /analyze/video`

Extracts frames from a video and analyzes each frame before generating an overall authenticity score.

**Request** — `multipart/form-data`

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | video file | Yes | Accepted formats: `mp4`, `mov`, `avi`, `mkv` |

Maximum upload size: 50 MB (configurable via `MAX_UPLOAD_SIZE`).

**Response** — `200 OK`

```json
{
  "status": "success",
  "analysis": {
    "prediction": "Real",
    "confidence": 74.32,
    "frames_analyzed": 11,
    "real_frames": 11,
    "fake_frames": 0,
    "trust_score": 74,
    "risk_level": "MEDIUM"
  }
}
```

**Error Responses**

Follows the standard [Error Format](#error-format) above — typically a `400` for an unsupported format or oversized file, or a `500` for an internal error.

---

### Text Analysis

`POST /analyze/text`

Analyzes submitted text for misinformation.

**Request** — `application/json`

| Field | Type | Required | Notes |
|---|---|---|---|
| `text` | string | Yes | The text content to analyze |

```json
{
  "text": "..."
}
```

**Response** — `200 OK`

```json
{
  "status": "success",
  "analysis": {
    "prediction": "Fake",
    "confidence": 99.79,
    "trust_score": 0,
    "risk_level": "HIGH"
  }
}
```

**Error Responses**

Follows the standard [Error Format](#error-format) above — typically a `400` for a missing or invalid `text` field, or a `500` for an internal error.

---

### Health Check

`GET /health`

Returns the current backend status. Useful for uptime monitoring and load balancer health checks.

**Response** — `200 OK`

```json
{
  "status": "healthy",
  "application": {
    "name": "Project ARGUS",
    "version": "1.1.0"
  },
  "system": {
    "device": "cuda",
    "cuda_available": true
  }
}
```

---

### Root Endpoint

`GET /`

Returns basic information about the running service, such as the application name and version.

---

## HTTP Status Codes

| Code | Meaning |
|---|---|
| `200` | Success |
| `400` | Bad Request |
| `404` | Not Found |
| `500` | Internal Server Error |

---

## Versioning

Project ARGUS follows [Semantic Versioning](https://semver.org/). The current backend version is `1.1.0`. For a full history of changes, see [CHANGELOG.md](CHANGELOG.md).