from config.settings import settings


def test_settings_load():
    assert settings.APP_NAME == "Project ARGUS"
    assert settings.PORT > 0
    assert settings.MAX_UPLOAD_SIZE > 0
    assert settings.DEVICE in ("cuda", "cpu")