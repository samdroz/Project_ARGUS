import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Project ARGUS")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.2.0")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Uploads
    UPLOAD_FOLDER: str = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50 MB default

    # AI Models
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "Wvolf/ViT_Deepfake_Detection")
    TEXT_MODEL: str = os.getenv("TEXT_MODEL", "hamzab/roberta-fake-news-classification")
    AUDIO_MODEL: str = os.getenv("AUDIO_MODEL", "")  # Optional: defaults to deterministic acoustic analyzer

    # Device preference
    DEVICE: str = os.getenv("DEVICE", "cuda")

    # Video processing
    VIDEO_FRAME_INTERVAL: int = int(os.getenv("VIDEO_FRAME_INTERVAL", "30"))
    VIDEO_MAX_FRAMES: int = int(os.getenv("VIDEO_MAX_FRAMES", "20"))

    # Audio processing
    AUDIO_MAX_DURATION_SEC: int = int(os.getenv("AUDIO_MAX_DURATION_SEC", "60"))

    # Search & Evidence Retrieval
    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "duckduckgo")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")
    BING_API_KEY: str = os.getenv("BING_API_KEY", "")

    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "*").split(",") if origin.strip()
    ]


settings = Settings()