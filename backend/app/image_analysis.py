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
    }
    
    scores = [float(metric[1]) for metric in metrics.values() if isinstance(metric, tuple) and isinstance(metric[1], (int, float))]
    quality_score = compute_quality_score(scores)    
    metrics["quality_score"] = f"{quality_score}%"
    
    return metrics
