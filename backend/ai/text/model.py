from ai.model_manager import model_manager

MODEL_NAME = "Text Model"

def get_device():
    return model_manager.device

def get_tokenizer():
    if model_manager.text_tokenizer is None:
        model_manager.load_text_model()
    return model_manager.text_tokenizer

def get_model():
    if model_manager.text_model is None:
        model_manager.load_text_model()
    return model_manager.text_model