import streamlit as st
import requests
from PIL import Image

st.set_page_config(page_title="Analyse IA des Photos", page_icon="📷", layout="centered")

st.markdown("<h1 class='title'>📸 Analyse de la Qualité des Photos</h1>", unsafe_allow_html=True)

analysis_type = st.selectbox(
    "Choisissez une méthode d'analyse",
    ["OpenCV (Module 1)", "Modèle IA (Module 2)"]
)

if analysis_type == "Modèle IA (Module 2)":
    model_name = "microsoft/resnet-50"

st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📤 Téléversez une image", type=["jpg", "jpeg", "png"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Image Téléversée", use_column_width=True)

    files = {"file": uploaded_file.getvalue()}

    if analysis_type == "OpenCV (Module 1)":
        response = requests.post("http://backend:8000/analyze/opencv/", files=files)
    else:
        response = requests.post(f"http://backend:8000/analyze/model/?model_name={model_name}", files=files)

    if response.status_code == 200:
        result = response.json()
        st.success("✅ Analyse réussie !")

        st.write("### Résultats de l'analyse")

        if analysis_type == "OpenCV (Module 1)":
            for item in result["results"]:  # 📌 Parcourir la liste bien formatée
                st.write(f"**{item['label']}** (Score: {item['score']:.2f}%)")

            quality_score = float(result["quality_score"])
            st.progress(int(round(quality_score)))  # Arrondir et convertir en int
            st.write(f"**Qualité de l'image**: {quality_score:.2f}%")

        else:  # 📌 Gestion des modèles IA
            st.write("### Classification de l'image (Top 3 résultats)")
            for item in result["result"][:3]:  # 🔥 Top 3 résultats
                st.write(f"**{item['label'].capitalize()}** (Score: {item['score'] * 100:.2f}%)")

    else:
        st.error("❌ Erreur lors de l'analyse. Veuillez réessayer.")

