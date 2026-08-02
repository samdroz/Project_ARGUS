from transformers import AutoImageProcessor, AutoModelForImageClassification
import torch

MODEL_ID = "Wvolf/ViT_Deepfake_Detection"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Loading processor...")
processor = AutoImageProcessor.from_pretrained(MODEL_ID)

print("Loading model...")
model = AutoModelForImageClassification.from_pretrained(MODEL_ID)

model.to(device)
model.eval()

print("\n✅ Model loaded successfully!")
print("Device:", device)
print("Labels:", model.config.id2label)