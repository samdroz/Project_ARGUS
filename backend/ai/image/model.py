from ai.model_manager import model_manager

MODEL_NAME = "Image Model"

def get_device():
    return model_manager.device

def get_processor():
    if model_manager.image_processor is None:
        model_manager.load_image_model()
    return model_manager.image_processor

def get_model():
    if model_manager.image_model is None:
        model_manager.load_image_model()
    return model_manager.image_model