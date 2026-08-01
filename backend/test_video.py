from ai.video.extractor import extractor

frames = extractor.extract(
    "test.mp4",
    "frames"
)

print("\nExtracted Frames:")
print(frames)

print(f"\nTotal Frames Extracted: {len(frames)}")