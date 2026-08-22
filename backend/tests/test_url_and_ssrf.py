import pytest
from ai.url.validator import is_safe_url
from ai.fact_checker import classify_domain, deduplicate_sources


def test_ssrf_blocks_localhost():
    is_safe, reason = is_safe_url("http://localhost:8000/secret")
    assert not is_safe
    assert "forbidden" in reason.lower() or "internal" in reason.lower()


def test_ssrf_blocks_private_ips():
    private_ips = [
        "http://127.0.0.1/admin",
        "http://10.0.0.1/status",
        "http://192.168.1.1/config",
        "http://172.16.0.1/debug",
        "http://169.254.169.254/latest/meta-data/"
    ]
    for url in private_ips:
        is_safe, reason = is_safe_url(url)
        assert not is_safe, f"Failed to block private IP: {url}"


def test_ssrf_blocks_non_http_schemes():
    bad_schemes = [
        "file:///etc/passwd",
        "ftp://example.com/file",
        "gopher://example.com",
        "data:text/plain;base64,SGVsbG8="
    ]
    for url in bad_schemes:
        is_safe, reason = is_safe_url(url)
        assert not is_safe, f"Failed to block bad scheme: {url}"


def test_ssrf_allows_public_web_domains():
    safe_urls = [
        "https://www.wikipedia.org/wiki/Main_Page",
        "https://www.nature.com/articles/d41586-024-00001-x",
        "https://www.reuters.com/news"
    ]
    for url in safe_urls:
        is_safe, reason = is_safe_url(url)
        assert is_safe, f"False positive SSRF block for: {url} ({reason})"


def test_domain_classification():
    gov_info = classify_domain("cdc.gov")
    assert gov_info["source_type"] == "government"
    assert gov_info["source_quality"] == "HIGH"

    edu_info = classify_domain("mit.edu")
    assert edu_info["source_type"] == "academic"
    assert edu_info["source_quality"] == "HIGH"

    fact_info = classify_domain("snopes.com")
    assert fact_info["source_type"] == "fact-checker"
    assert fact_info["source_quality"] == "VERY_HIGH"

    wiki_info = classify_domain("wikipedia.org")
    assert wiki_info["source_type"] == "encyclopedia"


def test_source_deduplication():
    sources = [
        {"title": "Story 1", "url": "https://example.com/article?utm_source=twitter", "domain": "example.com"},
        {"title": "Story 1 Duplicate", "url": "https://example.com/article?utm_source=facebook", "domain": "example.com"},
        {"title": "Story 2", "url": "https://reuters.com/article", "domain": "reuters.com"}
    ]
    deduped = deduplicate_sources(sources)
    assert len(deduped) == 2
