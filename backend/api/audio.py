from fastapi import APIRouter, UploadFile, File, HTTPException

from utils.file_handler import save_uploaded_file
from services.audio_service import audio_service

router = APIRouter(
    prefix="/analyze",
    tags=["Audio Analysis"]
)

ALLOWED_EXTENSIONS = [".wav", ".mp3", ".ogg", ".flac"]


@router.post(
    "/audio",
    summary="Analyze Audio for Voice Clones & Synthetic Speech",
    description="Evaluates audio waveforms for spectral discontinuities, pitch rigidity, vocoder artifacts, and synthetic voice characteristics."
)
async def analyze_audio(file: UploadFile = File(...)):
    try:
        file_info = save_uploaded_file(file, ALLOWED_EXTENSIONS)
        return audio_service.analyze(file_info)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")