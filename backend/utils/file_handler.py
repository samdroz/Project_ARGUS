from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile

from config.settings import settings


UPLOAD_DIR = Path(settings.UPLOAD_FOLDER)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_uploaded_file(
    file: UploadFile,
    allowed_extensions: list
):

    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:

        raise ValueError(
            f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    unique_filename = f"{uuid4()}{extension}"

    save_path = UPLOAD_DIR / unique_filename

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {

        "file_id": unique_filename.split(".")[0],

        "filename": file.filename,

        "saved_filename": unique_filename,

        "path": str(save_path)

    }