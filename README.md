# 📷 Système d'Analyse de Qualité des Photos de Monuments

Ce projet est un système permettant d'évaluer automatiquement la qualité des photos de monuments en analysant différents critères comme la netteté, l'exposition et la composition.

## 🚀 Fonctionnalités
- 📸 **Upload d'images** via une interface Streamlit
- 🖼️ **Analyse automatique** de la qualité des images avec FastAPI
- 📊 **Critères évalués** : netteté, exposition, composition, etc.
- 🔧 **Interface simple et intuitive** avec Streamlit
- 🐳 **Déploiement facile avec Docker & Docker Compose**
- 🧠 **Module 1 : Analyse de qualité avec OpenCV**

## 📂 Structure du projet
```
photo_quality_ai/
├── backend/            # API FastAPI pour analyser les images
│   ├── app/
│   │   ├── main.py     # Serveur FastAPI
│   │   ├── models.py   # Modèles ML
│   │   ├── image_analysis.py    # Fonctions de traitement d'image via opencv
│   │   ├── requirements.txt
│   ├── Dockerfile
├── frontend/           # Interface Streamlit pour l'upload et l'affichage
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
├── docker-compose.yml  # Orchestration des services
├── .gitignore
├── README.md
```

## 🛠️ Installation et Exécution

### 📦 Prérequis
- [Docker](https://www.docker.com/) et [Docker Compose](https://docs.docker.com/compose/)

### 🔧 Lancer l'application
Dans le terminal, exécutez :
```bash
docker-compose up --build
```
Cela va :
- Construire et démarrer le **backend (FastAPI)** sur `http://localhost:8000`
- Construire et démarrer le **frontend (Streamlit)** sur `http://localhost:8501`

### 📂 Arrêter les conteneurs
```bash
docker-compose down
```

## 🖼️ Utilisation
1. **Accédez à l'interface Streamlit** : [http://localhost:8501](http://localhost:8501)
2. **Chargez une image** (formats supportés : `.jpg`, `.jpeg`, `.png`)
3. **Obtenez une analyse de la qualité** avec des recommandations

## 🔍 Développement
Si vous souhaitez exécuter les services manuellement sans Docker :

### 1️⃣ Démarrer le backend (FastAPI)
```bash
cd backend/app
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2️⃣ Démarrer le frontend (Streamlit)
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## ✨ Améliorations possibles
- 🤖 Amélioration du modèle d'analyse avec du Machine Learning
- 📊 Ajout de graphiques pour une meilleure visualisation des résultats
- 🔍 Optimisation des performances

## 📝 Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

🚀 **Créé avec ❤️ par Jimmy**
