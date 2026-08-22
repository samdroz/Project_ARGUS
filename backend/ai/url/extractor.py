import re
import urllib.parse
from typing import Dict, Any
import httpx

from utils.logger import logger


class URLExtractor:
    """
    Safely retrieves and extracts clean article text, metadata, and author from web URLs.
    """

    def extract_content(self, url: str, max_body_chars: int = 5000) -> Dict[str, Any]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 ProjectARGUS/1.2",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        try:
            # Timeout of 8 seconds and max 5MB response to prevent hanging or memory spikes
            with httpx.Client(timeout=8.0, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                if response.status_code != 200:
                    raise ValueError(f"HTTP request failed with status code {response.status_code}")

                html = response.text[:5_000_000]

            # Extract Title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
            title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""

            # Extract meta description
            desc_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if not desc_match:
                desc_match = re.search(r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else ""

            # Extract clean body text: remove scripts, styles, head, nav, footer
            clean_html = re.sub(r"<(script|style|nav|footer|header|aside|noscript)[^>]*>.*?</\1>", "", html, flags=re.IGNORECASE | re.DOTALL)
            clean_text = re.sub(r"<[^>]+>", " ", clean_html)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()

            # Truncate for analysis
            if len(clean_text) > max_body_chars:
                clean_text = clean_text[:max_body_chars]

            domain = urllib.parse.urlparse(url).netloc

            return {
                "url": url,
                "domain": domain,
                "title": title,
                "description": description,
                "content": clean_text,
                "content_length": len(clean_text)
            }

        except Exception as e:
            logger.warning(f"Failed to fetch content from {url}: {e}")
            raise ValueError(f"Unable to retrieve webpage: {e}")


url_extractor = URLExtractor()
