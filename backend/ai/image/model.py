from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

MODEL_NAME = "Wvolf/ViT_Deepfake_Detection"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

processor = AutoImageProcessor.from_pretrained(MODEL_NAME)

model = AutoModelForImageClassification.from_pretrained(MODEL_NAME)

model.to(DEVICE)
model.eval()