import re
from typing import Dict, Any, List


class TextAnalyzer:
    """
    Linguistic, stylistic, and lexical analysis for text content.
    Extracts structural claims and detects sensationalist / clickbait patterns.
    """

    CLICKBAIT_PATTERNS = [
        r"\b(shocking|you won't believe|unbelievable|mind[\s-]blowing|secret revealed|miracle cure)\b",
        r"\b(banned in|what they don't want you to know|conspiracy|illuminati|hidden truth)\b",
        r"\b(100% proof|undeniable proof|urgent alert|share this before it's deleted)\b"
    ]

    def analyze_style(self, text: str) -> Dict[str, Any]:
        """
        Analyze stylistic markers such as capitalization, punctuation, and sensationalism.
        """
        if not text:
            return {
                "sensationalism_score": 0,
                "all_caps_ratio": 0.0,
                "exclamation_count": 0,
                "question_count": 0,
                "clickbait_flags": []
            }

        total_chars = len(text)
        alpha_chars = [c for c in text if c.isalpha()]
        upper_chars = [c for c in text if c.isupper()]

        all_caps_ratio = round(len(upper_chars) / max(1, len(alpha_chars)), 3)
        exclamation_count = text.count("!")
        question_count = text.count("?")

        found_flags = []
        text_lower = text.lower()
        for pattern in self.CLICKBAIT_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                found_flags.extend(matches)

        # Compute heuristic sensationalism score (0 to 100)
        sensationalism_score = 0
        if all_caps_ratio > 0.3:
            sensationalism_score += 30
        elif all_caps_ratio > 0.15:
            sensationalism_score += 15

        if exclamation_count >= 3:
            sensationalism_score += 30
        elif exclamation_count >= 1:
            sensationalism_score += 15

        if found_flags:
            sensationalism_score += min(40, len(found_flags) * 20)

        sensationalism_score = min(100, sensationalism_score)

        return {
            "sensationalism_score": sensationalism_score,
            "all_caps_ratio": all_caps_ratio,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "clickbait_flags": list(set(found_flags))
        }

    def extract_claims(self, text: str, max_claims: int = 3) -> List[str]:
        """
        Segment text into prominent candidate factual assertions.
        """
        if not text:
            return []

        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        claims = []

        for sentence in sentences:
            s = sentence.strip()
            # Filter out very short or empty sentences
            if len(s.split()) >= 4 and len(s) >= 20:
                claims.append(s)
            if len(claims) >= max_claims:
                break

        if not claims and text.strip():
            claims = [text.strip()[:200]]

        return claims


text_analyzer = TextAnalyzer()
