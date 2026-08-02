from ai.model_manager import model_manager

MODEL_NAME = "Image Model"

DEVICE = model_manager.device

processor = model_manager.image_processor
model = model_manager.image_model