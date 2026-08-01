from .exif import extract_exif
from .hash import generate_sha256


class MetadataAnalyzer:

    def analyze(self, file_path: str):

        exif = extract_exif(file_path)

        file_hash = generate_sha256(file_path)

        return {

            "hash": file_hash,

            "metadata": exif

        }


metadata_analyzer = MetadataAnalyzer()