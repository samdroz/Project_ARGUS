import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    APP_NAME = os.getenv("APP_NAME")
    APP_VERSION = os.getenv("APP_VERSION")

    DEBUG = os.getenv("DEBUG") == "True"

    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

    IMAGE_MODEL = os.getenv("IMAGE_MODEL")
    TEXT_MODEL = os.getenv("TEXT_MODEL")

    DEVICE = os.getenv("DEVICE")

    MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE"))


settings = Settings()