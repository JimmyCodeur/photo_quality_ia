import pyiqa
import torch

PYIQA_MODELS = {
    "NIMA (VGG16-AVA)": "nima-vgg16-ava"
}

def load_nima_pyiqa():
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    nima_model = pyiqa.create_metric(PYIQA_MODELS["NIMA (VGG16-AVA)"], device=device)
    return nima_model

NIMA_MODEL = load_nima_pyiqa()
