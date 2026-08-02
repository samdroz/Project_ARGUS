from ai.text.detector import detect_text

result = detect_text(
    title="NASA confirms aliens landed in New York",
    content="Scientists officially confirmed that aliens landed yesterday."
)

print(result)