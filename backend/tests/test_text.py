from ai.text.detector import detect_text


def test_legacy_text_detection():
    res = detect_text(
        title="NASA aliens",
        content="Scientists confirmed discovery."
    )
    assert res["media_type"] == "text"
    assert "prediction" in res