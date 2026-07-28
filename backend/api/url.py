from fastapi import APIRouter

from api.schemas import URLRequest

router = APIRouter(
    prefix="/analyze",
    tags=["URL Analysis"]
)


@router.post("/url")
async def analyze_url(request: URLRequest):
    return {
        "status": "success",
        "url": str(request.url),
        "prediction": "Pending AI Analysis",
        "confidence": 0,
        "trust_score": 0
    }