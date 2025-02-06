from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io

app = FastAPI()

@app.post("/analyze/")
async def analyze_image(file: UploadFile = File(...)):
    image = Image.open(io.BytesIO(await file.read()))
    return {"message": "Analyse en cours"}