from transformers import pipeline
import ollama
from PIL import Image

def load_huggingface_model(model_name="microsoft/resnet-50"):
    """Charge un modèle de classification d'image depuis Hugging Face."""
    model = pipeline("image-classification", model=model_name)
    return model

def classify_image_huggingface(image_path, model_name="microsoft/resnet-50"):
    """Utilise un modèle Hugging Face pour classer une image."""
    model = load_huggingface_model(model_name)
    image = Image.open(image_path)
    result = model(image)
    return result

def classify_image_ollama(image_path, model_name="llava"):
    """Utilise un modèle Ollama pour classer une image."""
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": "Analyze the quality of this image.", "images": [img_bytes]}]
    )
    
    return response["message"]["content"] if "message" in response else "Erreur lors de l'analyse."
