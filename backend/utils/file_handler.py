from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
import shutil

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def save_uploaded_file(file: UploadFile, allowed_extensions: list):
    # Get file extension
    extension = Path(file.filename).suffix.lower()

    # Validate extension
    if extension not in allowed_extensions:
        raise ValueError(
            f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    # Generate unique filename
    unique_filename = f"{uuid4()}{extension}"

    # Full save path
    save_path = UPLOAD_DIR / unique_filename

    # Save file
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "file_id": unique_filename.split(".")[0],
        "filename": file.filename,
        "saved_filename": unique_filename,
        "path": str(save_path)
    }