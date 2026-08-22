from fastapi import APIRouter, HTTPException

from schemas.url import URLRequest
from services.url_service import url_service

router = APIRouter(
    prefix="/analyze",
    tags=["URL Analysis"]
)


@router.post(
    "/url",
    summary="Analyze Web Article & Verify URL Claims",
    description="Validates target URL against SSRF vulnerabilities, extracts article content, classifies domain credibility, and verifies factual claims."
)
async def analyze_url(request: URLRequest):
    try:
        url_str = str(request.url)
        return url_service.analyze(
            url=url_str,
            verify_claims=request.verify_claims if request.verify_claims is not None else True
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL analysis failed: {str(e)}")