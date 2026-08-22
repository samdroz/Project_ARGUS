from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class FileInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    saved_filename: Optional[str] = None
    path: Optional[str] = None


class SourceItem(BaseModel):
    title: str
    url: str
    domain: str
    source_type: str = "unknown"
    source_quality: str = "unknown"
    stance: str = "UNVERIFIED"
    snippet: Optional[str] = None
    retrieval_date: Optional[str] = None


class ClaimItem(BaseModel):
    claim_id: int
    claim_text: str
    verdict: str = "UNVERIFIED"
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    sources: List[SourceItem] = Field(default_factory=list)


class EvidenceInfo(BaseModel):
    status: str = "UNVERIFIED"
    provider: str = "none"
    sources_count: int = 0
    claims_verified: int = 0
    sources: List[SourceItem] = Field(default_factory=list)
    claims: List[ClaimItem] = Field(default_factory=list)


class TrustInfo(BaseModel):
    score: Optional[int] = None
    risk: str
    verdict: str
    recommendation: str
    factors: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class ProcessingInfo(BaseModel):
    time_ms: float
    device: str
    model: str


class StandardResponse(BaseModel):
    status: str = "success"
    analysis_id: Optional[str] = None
    media_type: str
    prediction: str
    confidence: float
    trust_score: Optional[int] = None
    risk_level: str
    verdict: str
    model: str
    file: Optional[FileInfo] = None
    analysis: Dict[str, Any] = Field(default_factory=dict)
    evidence: Optional[EvidenceInfo] = None
    claims: List[ClaimItem] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    forensics: Dict[str, Any] = Field(default_factory=dict)
    trust: Optional[TrustInfo] = None
    factors: List[str] = Field(default_factory=list)
    recommendation: str = ""
    limitations: List[str] = Field(default_factory=list)
    processing: Optional[ProcessingInfo] = None