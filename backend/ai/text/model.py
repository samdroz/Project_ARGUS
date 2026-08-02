from ai.model_manager import model_manager

MODEL_NAME = "Text Model"

DEVICE = model_manager.device

tokenizer = model_manager.text_tokenizer
model = model_manager.text_model