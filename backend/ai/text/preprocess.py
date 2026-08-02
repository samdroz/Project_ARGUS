def prepare_text(
    title: str,
    content: str
) -> str:
    """
    Format text for the RoBERTa fake news model.
    """

    return f"<title>{title}<content>{content}<end>"