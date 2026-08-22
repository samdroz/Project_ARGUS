from fastapi import APIRouter, UploadFile, File, HTTPException

from utils.file_handler import save_uploaded_file
from services.video_service import video_service

router = APIRouter(
    prefix="/analyze",
    tags=["Video Analysis"]
)

ALLOWED_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv", ".webm"]


@router.post(
    "/video",
    summary="Analyze Video for Deepfakes",
    description="Samples frames across video timeline, analyzes per-frame facial/forensic signals, and performs temporal aggregation."
)
async def analyze_video(file: UploadFile = File(...)):
    try:
        file_info = save_uploaded_file(file, ALLOWED_EXTENSIONS)
        return video_service.analyze(file_info)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video analysis failed: {str(e)}")