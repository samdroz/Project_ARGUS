from fastapi import APIRouter, UploadFile, File, HTTPException

from utils.file_handler import save_uploaded_file
from services.image_service import image_service

router = APIRouter(
    prefix="/analyze",
    tags=["Image Analysis"]
)

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]


@router.post(
    "/image",
    summary="Analyze Image for Deepfakes & Manipulation",
    description="Evaluates uploaded image using Vision Transformers (ViT) and deterministic Error Level Analysis (ELA) forensics."
)
async def analyze_image(file: UploadFile = File(...)):
    try:
        file_info = save_uploaded_file(file, ALLOWED_EXTENSIONS)
        return image_service.analyze(file_info)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")