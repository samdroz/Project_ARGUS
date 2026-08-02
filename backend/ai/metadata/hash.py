import hashlib


def generate_sha256(file_path: str) -> str:
    """
    Generate SHA-256 hash for a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()