from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class URLRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target web article or claim URL to analyze")
    verify_claims: Optional[bool] = Field(default=True, description="Whether to verify extracted claims with search evidence")
