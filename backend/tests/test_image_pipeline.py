import os
import pytest
from PIL import Image
import numpy as np

from ai.image.preprocess import load_image
from ai.image.forensics import image_forensics
from ai.image.detector import detect_image
from ai.metadata.analyzer import metadata_analyzer


def test_image_preprocessing_and_forensics(tmp_path):
    img_path = str(tmp_path / "test_sample.png")
    # Create simple synthetic test image
    img_arr = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
    pil_img = Image.fromarray(img_arr)
    pil_img.save(img_path)

    loaded = load_image(img_path)
    assert loaded.size == (200, 200)

    forensics = image_forensics.analyze(loaded)
    assert "ela" in forensics
    assert "frequency_analysis" in forensics
    assert "prediction" in forensics

    meta = metadata_analyzer.analyze(img_path)
    assert meta["file_size_bytes"] > 0
    assert meta["file_hash"] is not None


def test_image_corrupt_file_handling(tmp_path):
    bad_file = str(tmp_path / "corrupted.jpg")
    with open(bad_file, "wb") as f:
        f.write(b"NOT_A_REAL_IMAGE_DATA")

    with pytest.raises(ValueError):
        load_image(bad_file)
