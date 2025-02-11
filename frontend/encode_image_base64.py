import base64
import io

def encode_image_base64(image):
    """Convertit l'image en base64 pour OpenAI"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()