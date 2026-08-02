from fastapi import APIRouter

from schemas.text import TextRequest
from services.text_service import text_service

router = APIRouter(
    prefix="/analyze",
    tags=["Text Analysis"]
)


@router.post("/text")
async def analyze_text(request: TextRequest):

    return text_service.analyze(
        title=request.title,
        content=request.content
    )