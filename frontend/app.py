import streamlit as st
import requests
from PIL import Image

# 🎨 Configuration générale
st.set_page_config(
    page_title="Analyse IA des Photos 📸",
    page_icon="📷",
    layout="wide"
)

# 🎨 CSS Custom pour le style
st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .upload-box {
        border: 2px dashed #ff4b4b;
        padding: 20px;
        text-align: center;
        background-color: #fff3f3;
        border-radius: 10px;
    }
    .stButton > button {
        background-color: #ff4b4b !important;
        color: white !important;
        border-radius: 8px !important;
        font-size: 18px !important;
        padding: 10px 20px !important;
    }
    .stProgress > div > div {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 🎯 TITRE PRINCIPAL
st.markdown("<h1 class='title'>📸 Analyse de la Qualité des Photos</h1>", unsafe_allow_html=True)

# 📌 Définition des modèles avec descriptions
ANALYSIS_MODELS = {
    "OpenCV (Module 1)": "Détection du flou avec OpenCV.",
    "NIMA (Module 2)": "NIMA (Neural Image Assessment) analyse l'esthétique perçue de la photo.",
    "LIQE (Module 3)": "Évaluation de la qualité technique avec LIQE."
}

# 📌 Sélection du module dans la barre latérale
st.sidebar.title("🔍 Paramètres d'analyse")
analysis_type = st.sidebar.radio("Sélectionnez une méthode :", list(ANALYSIS_MODELS.keys()))

# 📌 Affichage de la description du module sélectionné
st.sidebar.markdown("### ℹ️ Description du Modèle")
st.sidebar.write(ANALYSIS_MODELS[analysis_type])

# 📂 Téléversement de l’image
st.write("### 📂 Téléversez une image")
uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # 🎨 Affichage de l’image téléchargée
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Image Téléversée", use_container_width=True)

    files = {"file": uploaded_file.getvalue()}

    if st.button("🚀 Lancer l'analyse"):
        with st.spinner("Analyse en cours... ⏳"):
            # 📡 Requête API selon le modèle sélectionné
            if analysis_type == "OpenCV (Module 1)":
                response = requests.post("http://backend:8000/analyze/opencv/", files=files)
            elif analysis_type == "NIMA (Module 2)":
                response = requests.post("http://backend:8000/analyze/nima/", files=files)
            elif analysis_type == "LIQE (Module 3)":
                response = requests.post("http://backend:8000/analyze/liqe/", files=files)

            # 📌 Gestion de la réponse API
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Analyse réussie !")

                st.write("📊 **Données API reçues :**", result)
                st.write("### 📊 Résultats de l'analyse")

                # 📌 Résultat pour OpenCV
                if analysis_type == "OpenCV (Module 1)":
                    if "results" in result:
                        for item in result["results"]:
                            st.write(f"**{item['label']}** (Score: {item['score']:.2f}%)")

                    if "quality_score" in result:
                        try:
                            quality_score_percentage = float(result["quality_score"].replace('%', ''))
                            st.progress(int(round(quality_score_percentage)))
                            st.write(f"### 📌 **Score de qualité de l'image : {quality_score_percentage:.2f}%**")

                        except ValueError:
                            st.error("⚠️ Erreur : Impossible de convertir le score de qualité.")

                # 📌 Résultat pour NIMA (Module 2) avec seuil de qualité à 5.0
                elif analysis_type == "NIMA (Module 2)":
                    if "quality_score" in result:
                        try:
                            quality_score = float(result["quality_score"])
                            quality_score_percentage = quality_score * 10  # Conversion en pourcentage

                            st.progress(int(round(quality_score_percentage)))
                            st.write(f"### 📌 **Score de qualité esthétique de l'image : {quality_score_percentage:.2f}%**")

                            # Ajout de l'évaluation
                            if quality_score >= 5.0:
                                st.success("🟢 **L'image est de bonne qualité esthétique !** ✅")
                            else:
                                st.error("🔴 **L'image est de mauvaise qualité esthétique !** ❌")

                        except ValueError:
                            st.error("⚠️ Erreur : Impossible de convertir le score de qualité.")

                # 📌 Résultat pour LIQE (Module 3)
                elif analysis_type == "LIQE (Module 3)":
                    if "quality_score" in result:
                        try:
                            quality_score = float(result["quality_score"])
                            quality_score_percentage = quality_score * 10  # Conversion en pourcentage

                            st.progress(int(round(quality_score_percentage)))
                            st.write(f"### 📌 **Score de qualité technique de l'image : {quality_score_percentage:.2f}%**")

                        except ValueError:
                            st.error("⚠️ Erreur : Impossible de convertir le score de qualité.")

            else:
                st.error(f"❌ Erreur lors de l'analyse : {response.status_code}")
