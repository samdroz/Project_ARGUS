<div align="center">

# Project ARGUS

**Multi-modal AI platform for detecting fake news and deepfakes — with explainable trust scoring, not just a "fake" label.**

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![PyTorch](https://img.shields.io/badge/PyTorch-AI-red?logo=pytorch)
![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-yellow)
![CUDA](https://img.shields.io/badge/GPU-CUDA-green)
![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)

[Highlights](#project-highlights) · [Quick Start](#quick-start) · [API Reference](#api-reference) · [Roadmap](#roadmap) · [Report a Bug](../../issues)

</div>

---

### Demo

🎬 *A walkthrough GIF showing a live request and its trust-score response will go here once the dashboard ships. In the meantime, spin up the backend and explore every endpoint interactively through the built-in Swagger UI at `/docs`.*

---

## Project Highlights

- **One API, three modalities** — text, image, and video verification behind a single, consistent interface instead of three separate tools.
- **Explainable by default** — every result returns a trust score, a risk level, a confidence value, and the specific factors behind the verdict, not just "real" or "fake."
- **Modular model layer** — image, video, and text inference run as independent services behind a model manager, so any individual model can be upgraded or swapped without touching the API surface.
- **GPU-accelerated inference** — CUDA support out of the box for faster turnaround on image and video workloads.
- **Fully documented API** — interactive Swagger / OpenAPI docs generated automatically from the FastAPI backend, no separate docs site to maintain.

---

## The Problem

Misinformation today isn't confined to one format. A false claim can travel as a manipulated headline, an AI-generated image, or a deepfake video — and most detection tools only look at one of those at a time. Worse, they tend to return a bare "real" or "fake" verdict with no reasoning behind it, which makes the output hard to trust and even harder to act on.

## The Solution

ARGUS is a single backend that evaluates **text, images, and video** through purpose-built models, then runs every result through a **Trust Engine** that produces a score, a risk level, and a plain-language explanation of *why*. It's designed to sit underneath a product — a moderation tool, a browser extension, a newsroom workflow — rather than function as a standalone demo.

- **Text** — fine-tuned RoBERTa classifier for fake news detection
- **Images** — Vision Transformer for AI-generated / manipulated image detection
- **Video** — frame-level extraction and analysis, aggregated into an overall authenticity score
- **Trust Engine** — score, risk level, confidence, explainable factors, and a recommendation, instead of a binary label
- **Metadata analysis** — pulls available file metadata into the verification context
- **GPU acceleration** — CUDA-backed inference via PyTorch

---

## Screenshots

📸 *Swagger UI walkthroughs and sample trust-score responses will be added here as the project's frontend and documentation mature. Until then, `/docs` gives you a live, interactive view of every endpoint after you run the server locally.*

---

## Architecture

```
User Uploads Media
        │
        ▼
  FastAPI Backend
        │
        ▼
   Service Layer
   ┌────┼────┐
   ▼    ▼    ▼
 Image Video Text
  AI    AI    AI
   └────┼────┘
        ▼
  Trust Engine
        ▼
Standardized JSON Response
```

*A dedicated architecture diagram is in progress — the flow above reflects the current request pipeline accurately in the meantime.*

**Request flow:** Upload → Validation → Preprocessing → Model Inference → Trust Engine → Recommendation → JSON Response

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend / API | FastAPI, Python |
| AI / ML | PyTorch, Hugging Face Transformers |
| Computer Vision | OpenCV |
| NLP | RoBERTa |
| Acceleration | CUDA |
| API Docs | Swagger UI / OpenAPI |

**Models in production:**

| Media | Model |
|---|---|
| Image | `Wvolf/ViT_Deepfake_Detection` |
| Video | ViT + frame extraction |
| Text | `hamzab/roberta-fake-news-classification` |
| Audio | In progress |

---

## Quick Start

```bash
# Clone
git clone https://github.com/samdroz/Project_ARGUS.git
cd Project_ARGUS/backend

# Set up environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
APP_NAME=Project ARGUS
APP_VERSION=1.1.0

HOST=127.0.0.1
PORT=8000

IMAGE_MODEL=Wvolf/ViT_Deepfake_Detection
TEXT_MODEL=hamzab/roberta-fake-news-classification

DEVICE=cuda
MAX_UPLOAD_SIZE=52428800
```

Run it:

```bash
uvicorn main:app --reload
```

Interactive API docs: `http://127.0.0.1:8000/docs`

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/analyze/image` | POST | Analyze an uploaded image |
| `/analyze/video` | POST | Analyze an uploaded video |
| `/analyze/text` | POST | Analyze submitted text |
| `/health` | GET | Health check |
| `/` | GET | Root / service info |

**Example response**

```json
{
  "status": "success",
  "media_type": "image",
  "file": {
    "id": "...",
    "name": "image.jpg"
  },
  "analysis": {
    "prediction": "Real",
    "confidence": 94.23
  },
  "trust": {
    "score": 94,
    "risk": "LOW",
    "confidence": 94.23,
    "recommendation": "...",
    "factors": [
      "Very high model confidence.",
      "No major manipulation indicators detected."
    ]
  }
}
```

---

## Project Structure

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

## Roadmap

| Shipped | In Progress / Planned |
|---|---|
| Image deepfake detection | Audio deepfake detection |
| Video deepfake detection | URL verification |
| Fake news (text) detection | React dashboard |
| Trust Engine + explainability | Chrome extension |
| Metadata analysis | Docker support |
| Model manager, logging, health checks | Cloud deployment |

## Future Work

Near-term, the priority is rounding out modality coverage with audio deepfake detection and URL-level verification, so ARGUS can evaluate a claim regardless of how it's packaged. Beyond that, the focus shifts to accessibility and deployment: a React dashboard and Chrome extension to make the Trust Engine usable without touching the API directly, plus Docker support and a cloud deployment path so the backend can run outside a local GPU setup.

## Vision

ARGUS is built toward a single verification layer that any application can call into — a moderation pipeline, a newsroom tool, a browser extension — instead of maintaining separate detection stacks for every media type it handles. The modular model-manager design is deliberate: as stronger detection models emerge for any modality, they should be swappable without changing the API surface consumers already depend on.

---

## Contributing

Issues and PRs are welcome — this is early-stage and moving fast, so open an issue before starting on anything large so we can align on direction first.

## License

Released under the [MIT License](LICENSE).

---

<div align="center">

Built by **Sam Dharan Rozario** — backend architecture, AI integration, and model deployment.

[GitHub](https://github.com/samdroz) · [LinkedIn](https://linkedin.com/in/samdroz)

If ARGUS is useful to you, a ⭐ on the repo helps a lot.

</div>
