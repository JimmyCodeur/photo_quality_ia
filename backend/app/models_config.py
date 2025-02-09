import pyiqa
import torch

OPENAI_API_KEY = "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"

PYIQA_MODELS = {
    "NIMA (VGG16-AVA)": "nima-vgg16-ava",
    "LIQE (No-Reference)": "liqe"
}

def load_pyiqa_model(model_name):
    """Charge un modèle PyIQA donné."""
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    return pyiqa.create_metric(model_name, device=device)

PYIQA_INSTANCES = {name: load_pyiqa_model(model) for name, model in PYIQA_MODELS.items()}