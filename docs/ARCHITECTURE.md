# Project ARGUS — Architecture

This document explains the internal architecture of the Project ARGUS backend. It complements [README.md](README.md) (project overview) and [API.md](API.md) (public API reference).

## Table of Contents

- [Overview](#overview)
- [High-Level Architecture](#high-level-architecture)
- [Folder Structure](#folder-structure)
- [Layers](#layers)
  - [API Layer](#api-layer)
  - [Service Layer](#service-layer)
  - [AI Layer](#ai-layer)
  - [Model Manager](#model-manager)
  - [Trust Engine](#trust-engine)
- [Configuration](#configuration)
- [Logging](#logging)
- [Request Lifecycle](#request-lifecycle)
- [Scalability](#scalability)
- [Design Principles](#design-principles)
- [Versioning](#versioning)

---

## Overview

Project ARGUS follows a modular, service-oriented architecture. The backend separates:

- API Layer
- Service Layer
- AI Layer
- Trust Engine
- Utility Layer

This separation makes the project easier to extend, maintain, and test — each layer can change independently as long as it honors the interface the next layer expects.

## High-Level Architecture

```
                 User
                  │
                  ▼
          FastAPI REST API
                  │
                  ▼
             API Layer
                  │
                  ▼
          Service Layer
      ┌─────────┼─────────┐
      ▼         ▼         ▼
  Image      Video      Text
  Service    Service    Service
      │         │         │
      ▼         ▼         ▼
  Image AI   Video AI   Text AI
      └─────────┼─────────┘
                ▼
         Trust Engine
                ▼
      Standard Response
                ▼
           JSON Output
```

## Folder Structure

```
backend/
├── ai/
│   ├── image/
│   ├── video/
│   ├── text/
│   ├── metadata/
│   ├── trust/
│   └── model_manager.py
├── api/
├── config/
├── schemas/
├── services/
├── tests/
├── uploads/
├── utils/
├── main.py
├── requirements.txt
└── .env
```

---

## Layers

### API Layer

**Location:** `api/`

Responsible for:
- Receiving requests
- Validating input
- Invoking services
- Returning responses

### Service Layer

**Location:** `services/` — e.g. `image_service.py`, `video_service.py`, `text_service.py`

Contains the business logic between the API layer and the AI layer.

Responsibilities:
- Preprocessing
- Model execution
- Response generation

### AI Layer

**Location:** `ai/image/`, `ai/video/`, `ai/text/`, `ai/metadata/`, `ai/trust/`

Contains all AI models. Each module is isolated, so a given modality's model can be updated or replaced without touching the others.

### Model Manager

**Location:** `ai/model_manager.py`

Loads AI models once during application startup and shares them across requests.

Responsibilities:
- Load models
- Prevent duplicate loading
- GPU initialization
- Shared inference

### Trust Engine

**Location:** `ai/trust/`

Converts raw AI predictions into human-readable information.

Generates:
- Trust Score
- Risk Level
- Explainable Factors
- Recommendation

---

## Configuration

Application configuration is stored in `.env` and loaded through `config/settings.py`. This keeps secrets and environment-specific settings outside the source code. See the [README](README.md#quick-start) for the full list of configuration variables.

## Logging

Centralized logging captures:
- Startup events
- Model loading
- API requests
- Warnings
- Errors

## Request Lifecycle

```
     Upload
        │
        ▼
    Validation
        │
        ▼
   File Handler
        │
        ▼
   Service Layer
        │
        ▼
     AI Model
        │
        ▼
   Trust Engine
        │
        ▼
 Standard Response
        │
        ▼
   JSON Response
```

---

## Scalability

ARGUS is designed so additional modalities can be integrated without changing the existing API architecture. Planned additions include:

- Audio Detection
- URL Verification
- OCR
- Browser Extension
- Cloud Deployment

## Design Principles

- Modular
- Scalable
- Explainable
- Maintainable
- GPU Accelerated
- API First

---

## Versioning

The current backend architecture is aligned with version `1.1.0`. For a full history of changes, see [CHANGELOG.md](CHANGELOG.md).