from fastapi import APIRouter
from api.schemas import AnalysisResponse, TextRequest

router = APIRouter()


@router.post(
    "/analyze/text",
    response_model=AnalysisResponse
)
async def analyze_text(request: TextRequest):

    return AnalysisResponse(
        module="Text Detection",
        prediction="Fake",
        confidence=91.0,
        trust_score=82,
        message=f"Received {len(request.text)} characters. AI model not connected yet."
    )