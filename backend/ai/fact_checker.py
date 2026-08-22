import re
import socket
import urllib.parse
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

import httpx

from config.settings import settings
from config.constants import SourceCategory, EvidenceDirection, ClaimVerdict
from utils.logger import logger


# =====================================================================
# 1. Source Quality & Independence
# =====================================================================

FACT_CHECKING_DOMAINS = {
    "snopes.com", "politifact.com", "factcheck.org", "reuters.com",
    "apnews.com", "fullfact.org", "afp.com", "leadstories.com",
    "checkyourfact.com", "factcheck.afp.com"
}

REPUTABLE_NEWS_DOMAINS = {
    "bbc.com", "bbc.co.uk", "nytimes.com", "wsj.com", "washingtonpost.com",
    "theguardian.com", "bloomberg.com", "reuters.com", "apnews.com",
    "npr.org", "economist.com", "nature.com", "sciencemag.org",
    "scientificamerican.com"
}

ENCYCLOPEDIA_DOMAINS = {
    "wikipedia.org", "britannica.com"
}


def classify_domain(domain: str) -> Dict[str, str]:
    """
    Classify a domain's role, category, and baseline source quality.
    """
    domain_lower = domain.lower().strip()
    if domain_lower.startswith("www."):
        domain_lower = domain_lower[4:]

    # Government
    if domain_lower.endswith(".gov") or domain_lower.endswith(".mil") or domain_lower.endswith(".gov.uk"):
        return {
            "source_type": SourceCategory.GOVERNMENT,
            "source_quality": "HIGH",
            "role": "Primary / Official Public Record"
        }

    # Academic / Research
    if domain_lower.endswith(".edu") or domain_lower.endswith(".ac.uk"):
        return {
            "source_type": SourceCategory.ACADEMIC,
            "source_quality": "HIGH",
            "role": "Academic / Scientific Research"
        }

    # Fact-Checkers
    for fcd in FACT_CHECKING_DOMAINS:
        if domain_lower == fcd or domain_lower.endswith("." + fcd):
            return {
                "source_type": SourceCategory.FACT_CHECKER,
                "source_quality": "VERY_HIGH",
                "role": "Independent Fact-Checking Agency"
            }

    # Reputable News
    for rnd in REPUTABLE_NEWS_DOMAINS:
        if domain_lower == rnd or domain_lower.endswith("." + rnd):
            return {
                "source_type": SourceCategory.REPUTABLE_NEWS,
                "source_quality": "HIGH",
                "role": "Major News Organization"
            }

    # Encyclopedias
    for enc in ENCYCLOPEDIA_DOMAINS:
        if domain_lower == enc or domain_lower.endswith("." + enc):
            return {
                "source_type": SourceCategory.ENCYCLOPEDIA,
                "source_quality": "MODERATE_HIGH",
                "role": "Tertiary Encyclopedia"
            }

    return {
        "source_type": SourceCategory.UNKNOWN,
        "source_quality": "MODERATE",
        "role": "General Web Source"
    }


def normalize_source_url(url: str) -> str:
    """
    Strip tracking parameters to identify identical syndicated articles.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        # Strip common tracking query params
        qs = urllib.parse.parse_qsl(parsed.query)
        clean_qs = [(k, v) for k, v in qs if not k.startswith("utm_") and k not in ("ref", "fbclid", "gclid")]
        clean_query = urllib.parse.urlencode(clean_qs)
        return urllib.parse.urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), "", clean_query, ""))
    except Exception:
        return url


def deduplicate_sources(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter duplicate / syndicated sources by root domain and normalized URL.
    """
    seen_domains = set()
    seen_urls = set()
    deduped = []

    for src in sources:
        norm_url = normalize_source_url(src.get("url", ""))
        domain = src.get("domain", "").lower()

        if norm_url in seen_urls or domain in seen_domains:
            continue

        seen_urls.add(norm_url)
        seen_domains.add(domain)
        deduped.append(src)

    return deduped


# =====================================================================
# 2. Modular Search Providers
# =====================================================================

class BaseSearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        pass


class DuckDuckGoSearchProvider(BaseSearchProvider):
    """
    Free web search provider using DuckDuckGo HTML endpoint.
    """
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        try:
            with httpx.Client(timeout=6.0, follow_redirects=True) as client:
                response = client.post(url, data={"q": query}, headers=headers)
                if response.status_code != 200:
                    return []

                html = response.text
                results = []
                # Extract results using regex to avoid extra parser dependencies
                pattern = r'<a class="result__url"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?<a class="result__snippet"[^>]*>(.*?)</a>'
                matches = re.findall(pattern, html, re.DOTALL)

                for raw_url, raw_title, raw_snippet in matches:
                    clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
                    clean_snippet = re.sub(r"<[^>]+>", "", raw_snippet).strip()

                    # Resolve DDG redirect URL if present
                    actual_url = raw_url
                    if "uddg=" in raw_url:
                        try:
                            parsed_qs = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                            if "uddg" in parsed_qs:
                                actual_url = parsed_qs["uddg"][0]
                        except Exception:
                            pass

                    domain = urllib.parse.urlparse(actual_url).netloc
                    if not domain:
                        continue

                    classification = classify_domain(domain)

                    results.append({
                        "title": clean_title or domain,
                        "url": actual_url,
                        "domain": domain,
                        "snippet": clean_snippet,
                        "source_type": classification["source_type"],
                        "source_quality": classification["source_quality"],
                        "role": classification["role"],
                        "retrieval_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
                    })

                    if len(results) >= max_results:
                        break

                return deduplicate_sources(results)

        except Exception as e:
            logger.info(f"DuckDuckGo search unavailable ({e}). Operating in offline / unverified mode.")
            return []


class MockSearchProvider(BaseSearchProvider):
    """
    Mock search provider for isolated deterministic unit tests.
    """
    def __init__(self, predefined_results: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.predefined_results = predefined_results or {}

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        for key, res in self.predefined_results.items():
            if key.lower() in query.lower():
                return res[:max_results]
        return []


# =====================================================================
# 3. Claim Evaluator & Fact Checker Engine
# =====================================================================

class FactChecker:
    """
    Evidence Agent that extracts factual claims, executes targeted searches,
    classifies source credibility, and evaluates claim support vs contradiction.
    """

    def __init__(self, provider: Optional[BaseSearchProvider] = None):
        self.provider = provider or DuckDuckGoSearchProvider()

    def set_provider(self, provider: BaseSearchProvider):
        self.provider = provider

    def evaluate_stance(self, claim_text: str, source_snippet: str, source_title: str) -> str:
        """
        Evaluate whether a source supports, contradicts, or is neutral towards a claim.
        """
        combined = f"{source_title} {source_snippet}".lower()
        claim_lower = claim_text.lower()

        # Contradiction indicators
        contradiction_cues = [
            "false", "debunk", "hoax", "incorrect", "refute", "untrue",
            "fake", "no evidence", "misleading", "fact check:", "pants on fire",
            "fabricated", "denies", "denied"
        ]

        # Support indicators
        support_cues = [
            "confirmed", "officially", "announced", "verified", "statement confirms",
            "published in", "report shows", "evidence shows", "true"
        ]

        has_contradiction = any(cue in combined for cue in contradiction_cues)
        has_support = any(cue in combined for cue in support_cues)

        if has_contradiction and not has_support:
            return EvidenceDirection.CONTRADICTS
        elif has_support and not has_contradiction:
            return EvidenceDirection.SUPPORTS
        elif has_contradiction and has_support:
            return EvidenceDirection.NEUTRAL
        return EvidenceDirection.UNVERIFIED

    def verify_claim(self, claim_id: int, claim_text: str) -> Dict[str, Any]:
        """
        Search evidence and evaluate verdict for a single atomic claim.
        """
        search_query = f"{claim_text}"
        sources = self.provider.search(search_query, max_results=4)

        if not sources:
            return {
                "claim_id": claim_id,
                "claim_text": claim_text,
                "verdict": ClaimVerdict.UNVERIFIED,
                "confidence": 0.0,
                "reasoning": "No external independent sources found for this claim.",
                "sources": []
            }

        evaluated_sources = []
        contradict_count = 0
        support_count = 0

        for src in sources:
            stance = self.evaluate_stance(claim_text, src.get("snippet", ""), src.get("title", ""))
            src["stance"] = stance
            evaluated_sources.append(src)

            if stance == EvidenceDirection.CONTRADICTS:
                contradict_count += 1
            elif stance == EvidenceDirection.SUPPORTS:
                support_count += 1

        if contradict_count > support_count:
            verdict = ClaimVerdict.CONTRADICTED
            reasoning = f"Refuted by {contradict_count} independent source(s)."
            conf = 85.0
        elif support_count > contradict_count:
            verdict = ClaimVerdict.SUPPORTED
            reasoning = f"Corroborated by {support_count} independent source(s)."
            conf = 88.0
        elif support_count > 0 and contradict_count > 0:
            verdict = ClaimVerdict.MIXED
            reasoning = "Mixed evidence found across multiple sources."
            conf = 50.0
        else:
            verdict = ClaimVerdict.UNVERIFIED
            reasoning = "Retrieved sources were inconclusive or neutral."
            conf = 30.0

        return {
            "claim_id": claim_id,
            "claim_text": claim_text,
            "verdict": verdict,
            "confidence": conf,
            "reasoning": reasoning,
            "sources": evaluated_sources
        }

    def verify_text_claims(self, claims_text_list: List[str]) -> Dict[str, Any]:
        """
        Verify multiple claims and produce an aggregate EvidenceInfo block.
        """
        if not claims_text_list:
            return {
                "status": "UNVERIFIED",
                "provider": self.provider.__class__.__name__,
                "sources_count": 0,
                "claims_verified": 0,
                "sources": [],
                "claims": []
            }

        verified_claims = []
        all_sources = []

        for idx, claim_str in enumerate(claims_text_list, 1):
            claim_res = self.verify_claim(idx, claim_str)
            verified_claims.append(claim_res)
            all_sources.extend(claim_res.get("sources", []))

        deduped_sources = deduplicate_sources(all_sources)

        # Aggregate evidence verdict
        verdicts = [c["verdict"] for c in verified_claims]
        if ClaimVerdict.CONTRADICTED in verdicts:
            aggregate_status = "CONTRADICTED"
        elif all(v == ClaimVerdict.SUPPORTED for v in verdicts) and verdicts:
            aggregate_status = "SUPPORTED"
        elif ClaimVerdict.SUPPORTED in verdicts and ClaimVerdict.UNVERIFIED in verdicts:
            aggregate_status = "SUPPORTED"
        elif ClaimVerdict.MIXED in verdicts:
            aggregate_status = "MIXED"
        else:
            aggregate_status = "UNVERIFIED"

        return {
            "status": aggregate_status,
            "provider": self.provider.__class__.__name__,
            "sources_count": len(deduped_sources),
            "claims_verified": len(verified_claims),
            "sources": deduped_sources,
            "claims": verified_claims
        }


fact_checker = FactChecker()
