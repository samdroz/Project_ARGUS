from fastapi import APIRouter, UploadFile, File, HTTPException

from utils.file_handler import save_uploaded_file

router = APIRouter(
    prefix="/analyze",
    tags=["Image Analysis"]
)

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]


@router.post("/image")
async def analyze_image(file: UploadFile = File(...)):
    try:
        file_info = save_uploaded_file(file, ALLOWED_EXTENSIONS)

        return {
            "status": "success",
            "file_id": file_info["file_id"],
            "filename": file_info["filename"],
            "prediction": "Pending AI Analysis",
            "confidence": 0,
            "trust_score": 0
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))