from pydantic import BaseModel
from pydantic import BaseModel, HttpUrl

class URLRequest(BaseModel):
    url: HttpUrl


class AnalysisResponse(BaseModel):
    module: str
    prediction: str
    confidence: float
    trust_score: int
    message: str


class TextRequest(BaseModel):
    text: str