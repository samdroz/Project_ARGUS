import re


def clean_text(text: str) -> str:
    """
    Clean and normalize input text.
    """
    if not text:
        return ""
    # Normalize excessive whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def prepare_text(title: str, content: str, max_chars: int = 4000) -> str:
    """
    Combine title and content for text analysis with safe length truncation.
    """
    clean_t = clean_text(title)
    clean_c = clean_text(content)

    if clean_t and clean_c:
        combined = f"{clean_t} - {clean_c}"
    elif clean_c:
        combined = clean_c
    else:
        combined = clean_t

    if len(combined) > max_chars:
        combined = combined[:max_chars]

    return combined