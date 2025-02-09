import pyiqa
import torch
import openai
import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
from app.image_analysis import detect_blur, validate_image, compute_quality_score
from app.models_config import PYIQA_INSTANCES, OPENAI_API_KEY, PYIQA_MODELS
from app.encode_image import encode_image

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def load_pyiqa_model(model_name):
    """Charge un modèle PyIQA donné."""
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    return pyiqa.create_metric(model_name, device=device)

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

        nima_model = PYIQA_INSTANCES["NIMA (VGG16-AVA)"]
        score = nima_model(image)

        print("Résultat brut de NIMA :", score)

        return {
            "method": "nima",
            "model": "NIMA (VGG16-AVA)",
            "raw_score": score.tolist(),  
            "quality_score": f"{score.item():.2f}"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/analyze/liqe/")
async def analyze_liqe(file: UploadFile = File(...)):
    """Analyse la qualité technique d'une image avec LIQE (via PyIQA)."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")

        liqe_model = PYIQA_INSTANCES["LIQE (No-Reference)"]
        score = liqe_model(image)

        print(f"🔎 Score brut LIQE : {score}")

        return {
            "method": "liqe",
            "model": "LIQE (Qualité Technique)",
            "quality_score": f"{score.item():.2f}"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/analyze/openia-solo/")
async def analyze_gpt4o(file: UploadFile = File(...)):
    """Analyse d'image avec GPT-4o-mini en envoyant l'image en base64."""
    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
        image_base64 = encode_image(image)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse d'images."},
                {"role": "user", "content": [
                    {"type": "text", "text": "decrit l'image en une ou deux phrase et Analyse la qualité de cette image et donne une note sur 100."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]}
            ],
            max_tokens=100
        )

        gpt_analysis = response.choices[0].message.content

        return {
            "method": "gpt-4o-mini",
            "final_analysis": gpt_analysis
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# @app.post("/analyze/gpt4o/")
# async def analyze_gpt4o(file: UploadFile = File(...)):
#     """Analyse d'image avec GPT-4o Mini en respectant la structure API OpenAI."""
#     try:
#         image = Image.open(io.BytesIO(await file.read())).convert("RGB")

#         image_base64 = encode_image(image)

#         nima_score = PYIQA_INSTANCES["NIMA (VGG16-AVA)"](image).item()
#         liqe_score = PYIQA_INSTANCES["LIQE (No-Reference)"](image).item()

#         nima_quality = "Bonne qualité esthétique" if nima_score >= 5 else "Moins bonne qualité esthétique"
#         liqe_quality = "Bonne qualité technique" if liqe_score >= 5 else "Moins bonne qualité technique"

#         response = openai_client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "Vous êtes un expert en analyse de qualité d'image."},
#                 {"role": "user", "content": f"L'image a les scores suivants :\n"
#                                             f"- Score esthétique NIMA : {nima_score:.2f}/10 → {nima_quality}\n"
#                                             f"- Score technique LIQE : {liqe_score:.2f}/10 → {liqe_quality}\n\n"
#                                             f"Donne une **note finale sur 100** en tenant compte de ces scores et de l'image."},
#                 {"role": "user", "content": [{"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}]}
#             ],
#             max_tokens=100
#         )

#         gpt_analysis = response.choices[0].message.content

#         return {
#             "method": "gpt-4o-mini",
#             "quality_score_nima": f"{nima_score:.2f}",
#             "quality_score_liqe": f"{liqe_score:.2f}",
#             "final_analysis": gpt_analysis
#         }

#     except Exception as e:
#         return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
