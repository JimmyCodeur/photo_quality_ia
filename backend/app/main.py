import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
from app.image_analysis import detect_blur, validate_image, compute_quality_score
from app.models_config import PYIQA_MODELS, NIMA_MODEL

app = FastAPI()

@app.get("/models/")
async def get_models():
    """Récupère la liste des modèles disponibles."""
    return {
        "pyiqa_models": PYIQA_MODELS
    }

@app.post("/analyze/opencv/")
async def analyze_opencv(file: UploadFile = File(...)):
    """Analyse une image avec OpenCV pour détecter le flou. Le résultat est un score en %."""
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
            "results": [
                {"label": "Flou", "score": blur_result[1] * 100}, 
            ],
            "quality_score": f"{quality_score:.2f}%"
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/nima/")
async def analyze_nima(file: UploadFile = File(...)):
    """Analyse la qualité d'une image avec le modèle NIMA (via Pyiqa)."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")

        score = NIMA_MODEL(image)

        return {
            "method": "nima",
            "model": "NIMA (VGG16-AVA)",
            "quality_score": f"{score.item():.2f}"
        }
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
