import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Analyse IA des Photos", page_icon="📷", layout="centered")

st.markdown("<h1 class='title'>📸 Analyse de la Qualité des Photos</h1>", unsafe_allow_html=True)

models_response = requests.get("http://backend:8000/models/")
if models_response.status_code == 200:
    models_data = models_response.json()
else:
    st.error("❌ Impossible de récupérer les modèles disponibles.")
    models_data = {"huggingface_models": [], "ollama_models": []}

analysis_methods = ["OpenCV (Module 1)", "NIMA (Module 2)"]

analysis_type = st.selectbox("🔍 Choisissez une méthode d'analyse", analysis_methods)

st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📤 Téléversez une image", type=["jpg", "jpeg", "png"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Image Téléversée", use_container_width=True)

    files = {"file": uploaded_file.getvalue()}

    if analysis_type == "OpenCV (Module 1)":
        response = requests.post("http://backend:8000/analyze/opencv/", files=files)

    elif analysis_type == "NIMA (Module 2)":
        response = requests.post("http://backend:8000/analyze/nima/", files=files)

    if response.status_code == 200:
        result = response.json()
        st.success("✅ Analyse réussie !")

        st.write("📊 **Données API reçues :**", result)
        st.write("### 📊 Résultats de l'analyse")

        if analysis_type == "OpenCV (Module 1)":
            if "results" in result:
                for item in result["results"]:
                    st.write(f"**{item['label']}** (Score: {item['score']:.2f}%)")

            if "quality_score" in result:
                try:
                    quality_score = float(result["quality_score"].replace('%', ''))
                    quality_score = min(100, max(0, quality_score))
                    st.progress(int(round(quality_score)))
                    st.write(f"### 📌 Score de qualité de l'image : **{quality_score:.2f}**")

                    if quality_score >= 70:
                        st.success("🟢 L'image est **de bonne qualité** ✅")
                    elif 40 <= quality_score < 70:
                        st.warning("🟠 L'image est **moyenne** ⚠️")
                    else:
                        st.error("🔴 L'image est **de mauvaise qualité** ❌")

                except ValueError:
                    st.error("⚠️ Erreur : Impossible de convertir le score de qualité.")

        elif analysis_type == "NIMA (Module 2)":
            if "quality_score" in result:
                try:
                    quality_score = float(result["quality_score"])
                    st.write(f"### 📌 Score de qualité de l'image : **{quality_score:.2f}**")

                    if quality_score >= 5.5:
                        st.success("🟢 L'image est **de bonne qualité** ✅")
                    elif 5.0 <= quality_score < 5.5:
                        st.warning("🟠 L'image est **moyenne** ⚠️")
                    else:
                        st.error("🔴 L'image est **de mauvaise qualité** ❌")

                except ValueError:
                    st.error("⚠️ Erreur : Impossible de convertir le score de qualité.")

            else:
                st.warning("⚠️ Aucune donnée de qualité reçue du backend.")

    else:
        st.error(f"❌ Erreur lors de l'analyse : {response.status_code}")
