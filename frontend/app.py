import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Analyse de Qualité d'Image", page_icon="📷", layout="centered")

st.markdown("<h1 class='title'>📸 Analyse de la Qualité des Photos de Monuments</h1>", unsafe_allow_html=True)

st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📤 Téléversez une image", type=["jpg", "jpeg", "png"])
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Image Téléversée", use_container_width=True)

    files = {"file": uploaded_file.getvalue()}
    response = requests.post("http://backend:8000/analyze/opencv/", files=files)

    if response.status_code == 200:
        result = response.json()
        
        st.markdown("<div class='result-box'>", unsafe_allow_html=True)
        st.success("✅ Analyse réussie !")
        
        st.write("### Résultats de l'analyse")
        for key, value in result.items():
            if key != "quality_score":
                try:
                    score = float(value[1]) * 100  # Convertir en float
                    st.write(f"**{key.capitalize()}**: {value[0]} (Score: {score:.2f}%)")
                except ValueError:
                    st.write(f"**{key.capitalize()}**: {value}")  # En cas d'erreur, afficher la valeur brute

        
        st.write("### Score global de qualité")
        st.progress(min(100, max(0, int(float(result["quality_score"].replace('%', ''))))))

        st.write(f"**Qualité de l'image**: {result['quality_score']}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("❌ Erreur lors de l'analyse. Veuillez réessayer.")
