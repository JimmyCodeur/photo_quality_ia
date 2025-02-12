import pyiqa
import torch
import openai
import os
import io
import re
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from PIL import Image
import uvicorn
from app.image_analysis import detect_blur, validate_image, compute_quality_score
from app.models_config import PYIQA_INSTANCES, OPENAI_API_KEY, PYIQA_MODELS
from app.encode_image import encode_image_base64

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
IMAGE_DIR = "data/img/"

def load_pyiqa_model(model_name):
    """Charge un modèle PyIQA donné."""
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    return pyiqa.create_metric(model_name, device=device)
   
PYIQA_INSTANCES = {name: load_pyiqa_model(model) for name, model in PYIQA_MODELS.items()}

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backend en ligne via Ngrok"}

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

        clarity, blur_score = detect_blur(temp_path)
        blur_score = blur_score 

        scores = [blur_score]
        quality_score = compute_quality_score(scores)

        os.remove(temp_path)

        return {
            "method": "OpenCV",
            "results": [
                {"label": "Netteté", "score": blur_score},
                {"label": "Évaluation", "message": f"L'image est {clarity}"}
            ],
            "quality_score": f"{quality_score:.2f}%"
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
@app.post("/analyze/nima/")
async def analyze_nima(file: UploadFile = File(...)):
    """Analyse la qualité esthétique d'une image avec NIMA (via PyIQA)."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")

        nima_model = PYIQA_INSTANCES["NIMA (VGG16-AVA)"]
        score = nima_model(image).item() 

        quality_assessment = "Bonne qualité esthétique 👍" if score >= 5 else "Mauvaise qualité esthétique 👎"

        return {
            "method": "nima",
            "model": "NIMA (VGG16-AVA)",
            "raw_score": score,  
            "quality_score": f"{score:.2f}",
            "evaluation": quality_assessment
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/liqe/")
async def analyze_liqe(file: UploadFile = File(...)):
    """Analyse la qualité technique d'une image avec LIQE (via PyIQA)."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")

        liqe_model = PYIQA_INSTANCES["LIQE (No-Reference)"]
        score = liqe_model(image).item() 

        quality_assessment = "Bonne qualité technique 👍" if score >= 5 else "Mauvaise qualité technique 👎"

        return {
            "method": "liqe",
            "model": "LIQE (Qualité Technique)",
            "raw_score": score,
            "quality_score": f"{score:.2f}",
            "evaluation": quality_assessment
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    
@app.post("/analyze/openia-solo/")
async def analyze_gpt4o(image_url: str = Form(...)):
    """
    Analyse avancée d'image avec GPT-4o-mini.
    - Accepte **uniquement une URL d'image**.
    - Utilise `Form(...)` pour la validation.
    """
    try:
        if not image_url or not image_url.startswith(("http://", "https://")):
            return JSONResponse(content={"error": "L'URL de l'image est invalide. Fournissez un lien valide."}, status_code=400)

        prompt = """
        Tu es un expert en analyse de qualité d'image. 
        Évalue cette image en mettant une note sur 10 :
        - **Qualité technique** : netteté, bruit, exposition, couleurs.
        - **Qualité esthétique** : composition, équilibre, attrait visuel.
        
        🔹 **Note sur 100** : 
        Donne une note finale basée sur ces critères. 

        🔹 **Résumé en une phrase** : 
        Décris en 1 phrase ce que tu vois dans l'image.
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse d'images."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}} 
                ]}
            ],
            max_tokens=400
        )

        gpt_analysis = response.choices[0].message.content

        return {
            "method": "gpt-4o",
            "final_analysis": gpt_analysis
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/list-images/")
async def list_images():
    """Récupère la liste des images disponibles."""
    try:
        if os.path.exists(IMAGE_DIR):
            images = []
            for root, _, files in os.walk(IMAGE_DIR):
                for file in files:
                    if file.endswith((".jpg", ".jpeg", ".png")):
                        images.append(os.path.relpath(os.path.join(root, file), IMAGE_DIR))
            return {"images": images}
        return {"images": []}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/get-image/{image_path:path}")
async def get_image(image_path: str):
    """Récupère une image stockée dans le dossier backend."""
    try:
        file_path = os.path.join(IMAGE_DIR, image_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return JSONResponse(content={"error": "Image non trouvée"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/3-combined/")
async def analyze_combined(file: UploadFile = File(...)):
    """
    Analyse une image avec OpenCV (flou), NIMA (qualité esthétique) et LIQE (qualité technique).
    """
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        temp_path = "temp.jpg"
        image = image.resize((1024, 1024))
        image.save(temp_path)

        valid, error_msg = validate_image(temp_path)
        if not valid:
            return JSONResponse(content={"error": error_msg}, status_code=400)

        blur_result = detect_blur(temp_path)
        blur_score = blur_result[1] * 100
        clarity = "Flou" if blur_score >= 50 else "Net"

        nima_model = PYIQA_INSTANCES["NIMA (VGG16-AVA)"]
        nima_score = nima_model(image).item()
        nima_quality = "Bonne qualité esthétique 👍" if nima_score >= 5 else "Mauvaise qualité esthétique 👎"

        liqe_model = PYIQA_INSTANCES["LIQE (No-Reference)"]
        liqe_score = liqe_model(image).item()
        liqe_quality = "Bonne qualité technique 👍" if liqe_score >= 5 else "Mauvaise qualité technique 👎"

        os.remove(temp_path)

        return {
            "method": "Combined Analysis",
            "scores": {
                "opencv_blur": f"{blur_score:.2f}%",
                "nima_esthetic": f"{nima_score:.2f}",
                "liqe_technical": f"{liqe_score:.2f}"
            },
            "evaluation": {
                "clarity": f"L'image est {clarity}",
                "esthetic_quality": nima_quality,
                "technical_quality": liqe_quality
            },
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/4-combined/")
async def analyze_with_gpt(file: UploadFile = File(...), image_url: str = Form(...)):
    """
    Analyse une image avec OpenCV, NIMA et LIQE puis envoie l'analyse combinée à GPT-4o.
    """

    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        temp_path = "temp.jpg"
        image = image.resize((1024, 1024))
        image.save(temp_path)

        clarity, blur_raw_score = detect_blur(temp_path)
        blur_score = (1 - blur_raw_score) * 100 

        nima_model = PYIQA_INSTANCES["NIMA (VGG16-AVA)"]
        nima_score = nima_model(image).item()

        if nima_score >= 6:
            nima_quality = "Excellente qualité esthétique ⭐⭐⭐"
        elif 5 <= nima_score < 6:
            nima_quality = "Bonne qualité esthétique 👍"
        elif 3 <= nima_score < 5:
            nima_quality = "Qualité esthétique moyenne 🤔"
        else:
            nima_quality = "Mauvaise qualité esthétique 👎"

        liqe_model = PYIQA_INSTANCES["LIQE (No-Reference)"]
        liqe_score = liqe_model(image).item()
        liqe_quality = "Bonne qualité technique 👍" if liqe_score >= 5 else "Mauvaise qualité technique 👎"

        quality_score = compute_quality_score([blur_score, nima_score, liqe_score])

        combined_analysis = {
            "method": "Combined Analysis",
            "scores": {
                "opencv_blur": f"{blur_score:.2f}%", 
                "nima_esthetic": f"{nima_score:.2f}",
                "liqe_technical": f"{liqe_score:.2f}"
            },
            "evaluation": {
                "clarity": f"L'image est {clarity}",
                "esthetic_quality": nima_quality,
                "technical_quality": liqe_quality
            },
        }

        prompt = f"""
        Tu es un expert en analyse d'image.
        Voici l'évaluation technique et esthétique d'une image :

        - **Netteté détectée (OpenCV)** : {combined_analysis['scores']['opencv_blur']}
        - **Score esthétique (NIMA)** : {combined_analysis['scores']['nima_esthetic']}
        - **Score technique (LIQE)** : {combined_analysis['scores']['liqe_technical']}
        - **Clarté** : {combined_analysis['evaluation']['clarity']}
        - **Qualité esthétique** : {combined_analysis['evaluation']['esthetic_quality']}
        - **Qualité technique** : {combined_analysis['evaluation']['technical_quality']}

        🔍 **Analyse finale** :
        Donne ton analyse sur l'image et donne lui une note.
        **Note l’image sur 100** en prenant en compte tous ces critères et donne la note sous la forme "Score final : XX/100".
        """

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse d'images et en qualité visuelle."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]}
            ],
            max_tokens=400
        )

        gpt_analysis = response.choices[0].message.content

        score_match = re.search(r"Score final\s*:\s*(\d+)/100", gpt_analysis)
        gpt_final_score = int(score_match.group(1)) if score_match else None

        os.remove(temp_path)

        return {
            "method": "GPT-4o Image Analysis",
            "gpt_analysis": gpt_analysis,
            "combined_scores": combined_analysis,
            "gpt_final_score": gpt_final_score if gpt_final_score is not None else "Score non détecté"
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
