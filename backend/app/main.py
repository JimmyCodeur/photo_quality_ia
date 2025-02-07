import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
from app.image_analysis import (
    detect_blur, detect_noise, validate_image, compute_quality_score
)
from app.models import classify_image_huggingface, classify_image_ollama

app = FastAPI()

@app.post("/analyze/opencv/")
async def analyze_opencv(file: UploadFile = File(...)):
    """Analyse une image avec OpenCV pour détecter flou, bruit, etc. Le résultat est un score en %."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        temp_path = "temp.jpg"
        image = image.resize((1024, 1024))
        image.save(temp_path)

        valid, error_msg = validate_image(temp_path)
        if not valid:
            return JSONResponse(content={"error": error_msg}, status_code=400)

        blur_result = detect_blur(temp_path)
        noise_result = detect_noise(temp_path)

        scores = [blur_result[1], noise_result[1]]
        quality_score = compute_quality_score(scores)

        os.remove(temp_path)

        return {
            "method": "OpenCV",
            "results": [
                {"label": "Flou", "score": blur_result[1] * 100},  # Convertir en %
                {"label": "Bruit", "score": noise_result[1] * 100}  # Convertir en %
            ],
            "quality_score": quality_score
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/model/")
async def analyze_model(file: UploadFile = File(...), model_name: str = "microsoft/resnet-50", provider: str = "huggingface"):
    """
    Analyse une image en utilisant un modèle Hugging Face ou Ollama.
    - file: Image envoyée par l'utilisateur
    - model_name: Nom du modèle à utiliser
    - provider: "huggingface" ou "ollama"
    """
    try:
        image = Image.open(io.BytesIO(await file.read()))
        temp_path = "temp.jpg"
        image.save(temp_path)

        if provider == "huggingface":
            result = classify_image_huggingface(temp_path, model_name)
        elif provider == "ollama":
            result = classify_image_ollama(temp_path, model_name)
        else:
            return JSONResponse(content={"error": "Provider non supporté"}, status_code=400)

        os.remove(temp_path)

        return {"method": provider, "model": model_name, "result": result}
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
