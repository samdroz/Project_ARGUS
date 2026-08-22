from pathlib import Path
from uuid import uuid4
import shutil
import os
from fastapi import UploadFile

from config.settings import settings


UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(
    file: UploadFile,
    allowed_extensions: list,
    max_size: int = None
) -> dict:
    """
    Safely stream and save an uploaded file to disk with extension and size checks.
    """
    max_size = max_size or settings.MAX_UPLOAD_SIZE

    if not file.filename:
        raise ValueError("Uploaded file must have a valid filename.")

    extension = Path(file.filename).suffix.lower()
    if extension not in allowed_extensions:
        raise ValueError(
            f"Unsupported file type '{extension}'. Allowed: {', '.join(allowed_extensions)}"
        )

    unique_filename = f"{uuid4()}{extension}"
    save_path = UPLOAD_DIR / unique_filename

    # Stream chunks while enforcing max upload size
    bytes_written = 0
    with open(save_path, "wb") as buffer:
        while True:
            chunk = file.file.read(65536)  # 64KB chunks
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > max_size:
                # Cleanup partially written oversized file
                buffer.close()
                if os.path.exists(save_path):
                    os.remove(save_path)
                raise ValueError(
                    f"File exceeds maximum allowed upload size ({max_size / (1024 * 1024):.1f} MB)."
                )
            buffer.write(chunk)

    if bytes_written == 0:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise ValueError("Uploaded file is empty (0 bytes).")

    return {
        "file_id": unique_filename.split(".")[0],
        "filename": file.filename,
        "saved_filename": unique_filename,
        "path": str(save_path),
        "size_bytes": bytes_written
    }