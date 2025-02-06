import streamlit as st
import requests

st.title("Analyse de la qualité des photos de monuments")
uploaded_file = st.file_uploader("Téléversez une image", type=["jpg", "jpeg", "png"])
if uploaded_file:
    files = {"file": uploaded_file.getvalue()}
    response = requests.post("http://backend:8000/analyze/", files=files)
    st.json(response.json())