# Project Constants

PROJECT_NAME = "Project ARGUS"
API_VERSION = "1.2.0"

# Trust & Risk Enums
class RiskLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNKNOWN = "UNKNOWN"

class ClaimVerdict:
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    MIXED = "MIXED"
    UNVERIFIED = "UNVERIFIED"

class EvidenceDirection:
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    NEUTRAL = "NEUTRAL"
    UNVERIFIED = "UNVERIFIED"

class SourceCategory:
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    FACT_CHECKER = "fact-checker"
    REPUTABLE_NEWS = "reputable_news"
    ENCYCLOPEDIA = "encyclopedia"
    SECONDARY = "secondary_source"
    UNKNOWN = "unknown"

# Default fallback messages
NO_EVIDENCE_MESSAGE = "No corroborating or contradicting external evidence could be retrieved."