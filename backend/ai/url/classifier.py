from typing import Dict, Any
from ai.fact_checker import classify_domain


class URLClassifier:
    """
    Classify URL source authority, category, and credibility tier.
    """

    def classify(self, domain: str) -> Dict[str, Any]:
        return classify_domain(domain)


url_classifier = URLClassifier()
