from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.text import router as text_router
from api.image import router as image_router
from api.audio import router as audio_router
from api.video import router as video_router
from api.url import router as url_router

app = FastAPI(
    title="Project ARGUS API",
    description="AI-powered Multi-Modal Fake News & Deepfake Detection System",
    version="1.0.0"
)

# Register API routes
app.include_router(text_router)
app.include_router(image_router)
app.include_router(audio_router)
app.include_router(video_router)
app.include_router(url_router)

# Allow frontend to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # We'll restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "project": "Project ARGUS",
        "status": "Running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }