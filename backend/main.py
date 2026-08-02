from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

from api.text import router as text_router
from api.image import router as image_router
from api.audio import router as audio_router
from api.video import router as video_router
from api.url import router as url_router


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Multi-Modal Fake News & Deepfake Detection System",
    version="1.0.0",
    debug=settings.DEBUG
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(text_router)
app.include_router(image_router)
app.include_router(audio_router)
app.include_router(video_router)
app.include_router(url_router)


@app.get("/")
def root():

    return {
        "project": settings.APP_NAME,
        "status": "Running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }