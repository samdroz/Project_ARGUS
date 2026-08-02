from pydantic import BaseModel
from typing import Any, Dict, Optional


class FileInfo(BaseModel):
    id: Optional[str]
    name: str


class TrustInfo(BaseModel):
    score: int
    risk: str
    recommendation: str
    factors: list[str] = []


class ProcessingInfo(BaseModel):
    time_ms: float
    device: str
    model: str


class StandardResponse(BaseModel):
    status: str
    media_type: str
    file: FileInfo
    analysis: Dict[str, Any]
    metadata: Dict[str, Any]
    trust: TrustInfo
    processing: ProcessingInfo