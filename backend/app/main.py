import os
import io
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import uvicorn
from app.image_analysis import (
    detect_blur, detect_noise, detect_contrast, detect_brightness, detect_sharpness,
    validate_image, compute_quality_score
)

app = FastAPI()

@app.post("/analyze/opencv/")
async def analyze_opencv(file: UploadFile = File(...)):
    """Analyse une image avec OpenCV pour détecter flou, luminosité, contraste, bruit, balance des couleurs et cadrage."""
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
        contrast_result = detect_contrast(temp_path)
        brightness_result = detect_brightness(temp_path)
        sharpness_result = detect_sharpness(temp_path)

        scores = [
            blur_result[1], 
            noise_result[1],
            contrast_result[1],
            brightness_result[1],
            sharpness_result[1]
        ]
        quality_score = compute_quality_score(scores)
        
        os.remove(temp_path)

        return {
            "method": "OpenCV",
            "blur": blur_result,
            "noise": noise_result,
            "contrast": contrast_result,
            "brightness": brightness_result,
            "sharpness": sharpness_result,
            "quality_score": f"{quality_score}%"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
