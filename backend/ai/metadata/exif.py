from PIL import Image
from PIL.ExifTags import TAGS


def extract_exif(file_path: str) -> dict:
    """
    Extract EXIF metadata from an image.
    """

    try:

        image = Image.open(file_path)

        exif_data = image.getexif()

        metadata = {}

        for tag_id, value in exif_data.items():

            tag = TAGS.get(tag_id, tag_id)

            metadata[tag] = str(value)

        metadata["Width"] = image.width
        metadata["Height"] = image.height
        metadata["Format"] = image.format

        return metadata

    except Exception:

        return {
            "message": "No EXIF metadata found."
        }