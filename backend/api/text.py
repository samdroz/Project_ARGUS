from fastapi import APIRouter, HTTPException

from schemas.text import TextRequest
from services.text_service import text_service

router = APIRouter(
    prefix="/analyze",
    tags=["Text Analysis"]
)


@router.post(
    "/text",
    summary="Analyze Text & Verify Claims",
    description="Analyzes submitted text for stylistic misinformation markers and verifies extracted claims against external evidence."
)
async def analyze_text(request: TextRequest):
    try:
        if not request.content or not request.content.strip():
            raise HTTPException(status_code=400, detail="Content field cannot be empty.")

        return text_service.analyze(
            title=request.title or "",
            content=request.content,
            verify_claims=request.verify_claims if request.verify_claims is not None else True
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")