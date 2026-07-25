from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    module: str
    prediction: str
    confidence: float
    trust_score: int
    message: str


class TextRequest(BaseModel):
    text: str