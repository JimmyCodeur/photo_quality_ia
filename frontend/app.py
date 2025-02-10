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

st.markdown(
    """
    <style>
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
    }
    .image-container img {
        border-radius: 10px;
        max-width: 255px;
        max-height: 255px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("<h1 class='title'>📸 Analyse de la Qualité des Photos</h1>", unsafe_allow_html=True)

ANALYSIS_MODELS = {
    "OpenCV (Module 1)": "Détection du flou avec OpenCV.",
    "NIMA (Module 2)": "NIMA (Neural Image Assessment) analyse l'esthétique perçue de la photo.",
    "LIQE (Module 3)": "Évaluation de la qualité technique avec LIQE.",
    "GPT-4o-mini (Module 4)": "Analyse avancée IA avec OpenAI (via une URL d'image)."
}

st.sidebar.title("🔍 Paramètres d'analyse")
analysis_type = st.sidebar.radio("Sélectionnez une méthode :", list(ANALYSIS_MODELS.keys()))
st.sidebar.markdown("### ℹ️ Description du Modèle")
st.sidebar.write(ANALYSIS_MODELS[analysis_type])

if analysis_type == "GPT-4o-mini (Module 4)":
    image_url = st.text_input("🌐 Entrez l'URL d'une image pour l'analyse via https://postimages.org/ :")
else:
    response = requests.get(f"{BACKEND_URL}/list-images/")
    image_list = response.json().get("images", []) if response.status_code == 200 else []

    st.write("### 📂 Téléversez une image ou sélectionnez-en une existante")
    uploaded_file = st.file_uploader("Téléverser une image :", type=["jpg", "jpeg", "png"])
    selected_image = st.selectbox("📷 Ou sélectionnez une image :", ["Aucune"] + image_list, index=0)

image_bytes = None
image = None
selected_image_path = None

def process_image(image):
    """Convertit une image en RGB et la retourne en JPEG bytes sans compression."""
    img_buffer = io.BytesIO()
    try:
        image = image.convert("RGB") 
        image.save(img_buffer, format="JPEG", quality=100)
        return img_buffer.getvalue(), image 
    except Exception as e:
        st.error(f"❌ Erreur lors de la conversion de l'image : {str(e)}")
        return None, None

if analysis_type != "GPT-4o-mini (Module 4)":
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            image_bytes, image = process_image(image) 
            selected_image_path = None  
        except UnidentifiedImageError:
            st.error("❌ Erreur : L'image téléversée est invalide ou corrompue.")

    elif selected_image and selected_image != "Aucune":
        image_url = f"{BACKEND_URL}/get-image/{selected_image}"
        image_response = requests.get(image_url)

        if image_response.status_code == 200:
            try:
                image = Image.open(io.BytesIO(image_response.content))  
                image_bytes, image = process_image(image) 
                selected_image_path = selected_image
            except UnidentifiedImageError:
                st.error("❌ Erreur : L'image sélectionnée est invalide ou corrompue.")
                image_bytes = None
        else:
            st.error("❌ Erreur lors du chargement de l'image sélectionnée.")
            image_bytes = None

if image_bytes and analysis_type != "GPT-4o-mini (Module 4)":
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(image, caption="🖼️ Image originale", use_column_width=True) 
    st.markdown('</div>', unsafe_allow_html=True)

if image_bytes or (analysis_type == "GPT-4o-mini (Module 4)" and image_url):
    with st.expander("📋 Informations sur l'image sélectionnée", expanded=True):
        if analysis_type == "GPT-4o-mini (Module 4)":
            st.write(f"🌐 **URL de l'image :** {image_url}")
        else:
            st.write(f"📂 **Nom du fichier :** {selected_image_path if selected_image_path else 'Image Téléversée'}")
            st.write(f"📏 **Taille du fichier :** {len(image_bytes) / 1024:.2f} KB")

if st.button("🚀 Lancer l'analyse"):
    with st.spinner("🔎 Analyse en cours..."):
        if analysis_type == "GPT-4o-mini (Module 4)":
            if not image_url:
                st.error("❌ Veuillez entrer une URL d'image valide.")
            else:
                response = requests.post(f"{BACKEND_URL}/analyze/openia-solo/", data={"image_url": image_url})  
        else:
            files = {"file": ("image.jpg", image_bytes, "image/jpeg")}  
            if analysis_type == "OpenCV (Module 1)":
                response = requests.post(f"{BACKEND_URL}/analyze/opencv/", files=files)
            elif analysis_type == "NIMA (Module 2)":
                response = requests.post(f"{BACKEND_URL}/analyze/nima/", files=files)
            elif analysis_type == "LIQE (Module 3)":
                response = requests.post(f"{BACKEND_URL}/analyze/liqe/", files=files)

        if response.status_code == 200:
            result = response.json()
            st.success("✅ Analyse réussie !")
            st.write("📊 **Données API reçues :**", result)
        else:
            st.error(f"❌ Erreur lors de l'analyse : {response.status_code}")
