import pyiqa
import torch
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PYIQA_MODELS = {
    "NIMA (VGG16-AVA)": "nima-vgg16-ava",
    "LIQE (No-Reference)": "liqe"
}

def load_pyiqa_model(model_name):
    """Charge un modèle PyIQA donné."""
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    return pyiqa.create_metric(model_name, device=device)

PYIQA_INSTANCES = {name: load_pyiqa_model(model) for name, model in PYIQA_MODELS.items()}