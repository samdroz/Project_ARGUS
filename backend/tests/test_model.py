from ai.model_manager import model_manager


def test_model_manager_status():
    summary = model_manager.get_status_summary()
    assert "device" in summary
    assert "models" in summary
    assert "image" in summary["models"]
    assert "text" in summary["models"]