import torch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from utils.logger import logger

from ai.model_manager import model_manager

from api.image import router as image_router
from api.video import router as video_router
from api.text import router as text_router
from api.audio import router as audio_router
from api.url import router as url_router


# ---------------------------------------------------------
# Startup
# ---------------------------------------------------------

logger.info("Starting Project ARGUS Backend...")

model_manager.load_all()

logger.info("AI models loaded successfully.")


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Multi-Modal Fake News & Deepfake Detection System",
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)


# ---------------------------------------------------------
# Middleware
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Restrict in production
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
        "status": "Running"
    }


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
    summary="System Health Check"
)
def health():

    return {

        "status": "healthy",

        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION
        },

        "system": {
            "device": model_manager.device,
            "cuda_available": torch.cuda.is_available()
        },

        "models": {

            "image": (
                "loaded"
                if model_manager.image_model
                else "not_loaded"
            ),

            "text": (
                "loaded"
                if model_manager.text_model
                else "not_loaded"
            ),

            "audio": "not_loaded"

        },

        "services": {

            "trust_engine": "running",

            "metadata": "running",

            "report_service": "running"

        }

    }