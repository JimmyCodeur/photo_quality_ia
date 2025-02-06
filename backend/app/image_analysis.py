import cv2
import numpy as np

def detect_blur(image_path):
    """Détecte si une image est floue en utilisant la variance du Laplacien."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return "Erreur: Image non chargée", 0.0
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    return ("Flou", float(laplacian_var / 500)) if laplacian_var < 100 else ("Net", min(float(laplacian_var / 500), 1.0))

def detect_noise(image_path):
    """Détecte le bruit numérique dans l'image en mesurant la variance des pixels."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return "Erreur: Image non chargée", 0.0
    noise = np.var(image)
    score = float(min(1.0, 100 / (noise + 1)))
    return ("Beaucoup de bruit", score) if noise > 100 else ("Faible bruit", score)

def detect_contrast(image_path):
    """Analyse le contraste en utilisant la différence entre max et min de l'histogramme."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return "Erreur: Image non chargée", 0.0
    min_pixel, max_pixel = np.min(image), np.max(image)
    contrast = max_pixel - min_pixel
    score = float(min(1.0, contrast / 255))
    return ("Faible contraste", score) if contrast < 50 else ("Bon contraste", score)

def detect_brightness(image_path):
    """Évalue la luminosité moyenne de l'image."""
    image = cv2.imread(image_path)
    if image is None:
        return "Erreur: Image non chargée", 0.0
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    brightness = np.mean(hsv[:, :, 2])
    score = max(0.0, min(1.0, (brightness - 50) / 150))
    return ("Trop sombre", score) if brightness < 50 else ("Trop lumineux", score) if brightness > 200 else ("Correct", 1.0)

def detect_sharpness(image_path):
    """Mesure la netteté en évaluant la variance du filtre Sobel."""
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        return "Erreur: Image non chargée", 0.0
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
    sharpness = np.var(sobelx) + np.var(sobely)
    score = min(1.0, sharpness / 1000)
    return ("Netteté faible", score) if sharpness < 500 else ("Bonne netteté", score)

def validate_image(image_path):
    """Vérifie si une image est bien chargée et exploitable."""
    img = cv2.imread(image_path)
    if img is None:
        return False, "Image corrompue ou format non supporté"
    return True, "Image valide"

def compute_quality_score(scores):
    """Calcule un score de qualité global en pourcentage."""
    return round(float(np.mean(scores) * 100), 2) if scores else 0.0

def analyze_image_quality(image_path):
    """Effectue l'analyse complète de l'image et retourne un score global."""
    metrics = {
        "blur": detect_blur(image_path),
        "noise": detect_noise(image_path),
        "contrast": detect_contrast(image_path),
        "brightness": detect_brightness(image_path),
        "sharpness": detect_sharpness(image_path)
    }
    
    scores = [float(metric[1]) for metric in metrics.values() if isinstance(metric, tuple) and isinstance(metric[1], (int, float))]
    quality_score = compute_quality_score(scores)    
    metrics["quality_score"] = f"{quality_score}%"
    
    return metrics
