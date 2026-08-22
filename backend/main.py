from contextlib import asynccontextmanager
import os
from pathlib import Path
import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config.settings import settings
from utils.logger import logger
from ai.model_manager import model_manager

from api.image import router as image_router
from api.video import router as video_router
from api.text import router as text_router
from api.audio import router as audio_router
from api.url import router as url_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Project ARGUS Backend...")
    try:
        model_manager.load_all()
        logger.info("Model initialization pass completed.")
    except Exception as e:
        logger.error(f"Startup model load notice: {e}")
    yield
    # Shutdown
    logger.info("Project ARGUS Backend shutting down.")


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Multi-Modal Fake News, Deepfake & Claim Verification System",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Register Routes
# ---------------------------------------------------------

app.include_router(image_router)
app.include_router(video_router)
app.include_router(text_router)
app.include_router(audio_router)
app.include_router(url_router)

logger.info("All API routes registered successfully.")


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/", tags=["System"])
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "Running",
        "supported_modalities": ["text", "image", "video", "audio", "url"],
        "docs_url": "/docs"
    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
    summary="System & AI Health Check"
)
def health():
    summary = model_manager.get_status_summary()
    return {
        "status": "healthy",
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION
        },
        "system": {
            "device": summary["device"],
            "cuda_available": summary["cuda_available"],
            "cuda_device_name": summary["cuda_device_name"]
        },
        "models": summary["models"],
        "services": {
            "trust_engine": "active",
            "metadata_analyzer": "active",
            "evidence_agent": "active",
            "forensics": "active",
            "report_service": "active"
        }
    }


# ---------------------------------------------------------
# Frontend Static Files
# ---------------------------------------------------------

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    @app.get("/app", tags=["Frontend"], include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
    logger.info(f"Frontend mounted at /app from {FRONTEND_DIR}")