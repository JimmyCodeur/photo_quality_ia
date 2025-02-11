import streamlit as st
import requests
from PIL import Image, UnidentifiedImageError
import io

BACKEND_URL = "http://backend:8000"

st.set_page_config(
    page_title="Analyse IA des Photos 📸",
    page_icon="📷",
    layout="wide"
)

# ===================================================
# 🎛️ MENU DE NAVIGATION
# ===================================================
st.sidebar.title("📌 Navigation")
module = st.sidebar.radio(
    "Sélectionnez un module d'analyse",
    ["Module 1 - OpenCV", "Module 2 - NIMA (esthétique)", "Module 3 - LIQE (Technique)", 
     "Module 4 - GPT", "Module 5 - Analyse Combinée"]
)

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #ff4b4b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 class='title'>📸 Analyse de la Qualité des Photos</h1>", unsafe_allow_html=True)

# ===================================================
# 🟢 MODULES 1, 2 & 3 - ANALYSE PAR UPLOAD UNIQUEMENT
# ===================================================
if module in ["Module 1 - OpenCV", "Module 2 - NIMA (esthétique)", "Module 3 - LIQE (Technique)"]:
    st.markdown(f"<h2 style='color: #007BFF;'>🖼️ {module}</h2>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📤 Téléversez une image :", type=["jpg", "jpeg", "png"])
    image_bytes = None
    image = None

    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            img_buffer = io.BytesIO()
            image.convert("RGB").save(img_buffer, format="JPEG", quality=100)
            image_bytes = img_buffer.getvalue()
        except UnidentifiedImageError:
            st.error("❌ Erreur : L'image téléversée est invalide ou corrompue.")

    if st.button(f"🚀 Lancer l'analyse ({module})"):
        if image_bytes is None:
            st.error("❌ Aucune image n'a été chargée. Veuillez téléverser une image.")
        else:
            with st.spinner("🔎 Analyse en cours..."):
                files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
                endpoint = "/analyze/opencv/" if module == "Module 1 - OpenCV" else "/analyze/nima/" if module == "Module 2 - NIMA" else "/analyze/liqe/"
                response = requests.post(f"{BACKEND_URL}{endpoint}", files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analyse réussie !")
                    st.write("📊 **Données API reçues :**", result)
                else:
                    st.error(f"❌ Erreur lors de l'analyse : {response.status_code}")

# ===================================================
# 🔵 MODULE 4 - ANALYSE PAR URL UNIQUEMENT
# ===================================================
elif module == "Module 4 - GPT":
    st.markdown("<h2 style='color: #007BFF;'>🌍 Analyse basée sur une URL d'image</h2>", unsafe_allow_html=True)

    MEMORIZED_IMAGES = {
        "Statue De La Liberté": "https://i.postimg.cc/0yXGbvM7/a5e07ffa35.jpg",
        "Tour Eiffel": "https://i.postimg.cc/Cxt8KxBD/tower-103417-1280.jpg"
    }

    st.markdown("### 📌 Images mémorisées (à titre informatif)")
    for name, url in MEMORIZED_IMAGES.items():
        st.markdown(f"🔗 **{name}** : [{url}]({url})")

    image_url_4 = st.text_input("🌐 Entrez une URL d'image personnalisée :")

    if st.button("🚀 Lancer l'analyse (Module 4)"):
        if not image_url_4:
            st.error("❌ Veuillez entrer une URL d'image valide.")
        else:
            with st.spinner("🔎 Analyse en cours..."):
                response = requests.post(f"{BACKEND_URL}/analyze/openia-solo/", data={"image_url": image_url_4})

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analyse réussie !")
                    st.write("📊 **Données API reçues :**", result)
                else:
                    st.error(f"❌ Erreur lors de l'analyse : {response.status_code}")

# ===================================================
# 🔵 MODULE 5 - ANALYSE COMBINÉE AVEC URL & UPLOAD
# ===================================================
elif module == "Module 5 - Analyse Combinée":
    st.markdown("<h2 style='color: #007BFF;'>📂 Analyse combinée avec image téléversée + URL</h2>", unsafe_allow_html=True)

    uploaded_file_5 = st.file_uploader("📤 Téléversez une image :", type=["jpg", "jpeg", "png"])
    image_url_5 = st.text_input("🌐 Entrez une URL d'image personnalisée :")

    image_bytes_5 = None
    image_5 = None

    if uploaded_file_5:
        try:
            image_5 = Image.open(uploaded_file_5)
            img_buffer = io.BytesIO()
            image_5.convert("RGB").save(img_buffer, format="JPEG", quality=100)
            image_bytes_5 = img_buffer.getvalue()
        except UnidentifiedImageError:
            st.error("❌ Erreur : L'image téléversée est invalide ou corrompue.")

    if st.button("🚀 Lancer l'analyse (Module 5)"):
        if not image_url_5 or image_bytes_5 is None:
            st.error("❌ Veuillez téléverser une image et entrer une URL valide.")
        else:
            with st.spinner("🔎 Analyse en cours..."):
                files = {"file": ("image.jpg", image_bytes_5, "image/jpeg")}
                response = requests.post(f"{BACKEND_URL}/analyze/4-combined/", data={"image_url": image_url_5}, files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Analyse réussie !")
                    st.write("📊 **Données API reçues :**", result)
                else:
                    st.error(f"❌ Erreur lors de l'analyse : {response.status_code}")
