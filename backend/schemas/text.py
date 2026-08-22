from pydantic import BaseModel, Field
from typing import Optional


class TextRequest(BaseModel):
    title: Optional[str] = Field(default="", description="Headline or title of the text")
    content: str = Field(..., min_length=1, description="Body or text content to verify")
    verify_claims: Optional[bool] = Field(default=True, description="Whether to search for external evidence")