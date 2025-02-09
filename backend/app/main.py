import pyiqa
import torch
import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
from app.image_analysis import detect_blur, validate_image, compute_quality_score

# 📌 Modèles PyIQA disponibles
PYIQA_MODELS = {
    "NIMA (VGG16-AVA)": "nima-vgg16-ava",
    "LIQE (No-Reference)": "liqe"
}

# 📌 Fonction pour charger les modèles PyIQA
def load_pyiqa_model(model_name):
    """Charge un modèle PyIQA donné."""
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    return pyiqa.create_metric(model_name, device=device)

# 📌 Chargement des modèles
PYIQA_INSTANCES = {name: load_pyiqa_model(model) for name, model in PYIQA_MODELS.items()}

app = FastAPI()

@app.get("/models/")
async def get_models():
    """Récupère la liste des modèles disponibles."""
    return {
        "pyiqa_models": list(PYIQA_MODELS.keys())
    }

@app.post("/analyze/opencv/")
async def analyze_opencv(file: UploadFile = File(...)):
    """Analyse une image avec OpenCV pour détecter le flou."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        temp_path = "temp.jpg"
        image = image.resize((1024, 1024))
        image.save(temp_path)

        valid, error_msg = validate_image(temp_path)
        if not valid:
            return JSONResponse(content={"error": error_msg}, status_code=400)

        blur_result = detect_blur(temp_path)
        scores = [blur_result[1]]
        quality_score = compute_quality_score(scores)

        os.remove(temp_path)

        return {
            "method": "OpenCV",
            "results": [{"label": "Flou", "score": blur_result[1] * 100}],
            "quality_score": f"{quality_score:.2f}%"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/nima/")
async def analyze_nima(file: UploadFile = File(...)):
    """Analyse la qualité esthétique d'une image avec NIMA (via PyIQA)."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")

        # 📌 Utilisation correcte du modèle NIMA
        nima_model = PYIQA_INSTANCES["NIMA (VGG16-AVA)"]
        score = nima_model(image)

        # 🔍 Afficher le résultat brut dans la console du backend
        print("Résultat brut de NIMA :", score)

        return {
            "method": "nima",
            "model": "NIMA (VGG16-AVA)",
            "raw_score": score.tolist(),  # Résultat brut sous forme de liste
            "quality_score": f"{score.item():.2f}"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/liqe/")
async def analyze_liqe(file: UploadFile = File(...)):
    """Analyse la qualité technique d'une image avec LIQE (via PyIQA)."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")

        # 📌 Utilisation correcte du modèle LIQE
        liqe_model = PYIQA_INSTANCES["LIQE (No-Reference)"]
        score = liqe_model(image)

        # 🔍 Afficher les logs pour voir la sortie brute du modèle
        print(f"🔎 Score brut LIQE : {score}")

        return {
            "method": "liqe",
            "model": "LIQE (Qualité Technique)",
            "quality_score": f"{score.item():.2f}"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
