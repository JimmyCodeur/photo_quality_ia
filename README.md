### 📷 **Système d'Analyse de Qualité des Photos de Monuments**

Ce projet est un système permettant d'évaluer automatiquement la qualité des photos de monuments en analysant différents critères.

## 🚀 **Fonctionnalités**
- 📸 **Upload d'images** via une interface Streamlit
- 🎨 **Analyse automatique** de la qualité des images avec FastAPI
- 📊 **Critères évalués** : netteté, bruit, composition, score de qualité global
- 🧠 **Module 1 : Analyse de qualité avec OpenCV**
- 🤖 **Module 2 : Évaluation de la qualité avec NIMA (Neural Image Assessment)**
- 🔧 **Interface simple et intuitive** avec Streamlit
- 🐳 **Déploiement facile avec Docker & Docker Compose**

## 📂 **Structure du projet**
```
photo_quality_ai/
├── backend/          
│   ├── app/
│   │   ├── main.py    
│   │   ├── models_config.py   
│   │   ├── image_analysis.py    
│   │   ├── requirements.txt
│   ├── Dockerfile
├── frontend/          
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
├── docker-compose.yml 
├── .gitignore
├── README.md
```

## 🛠️ **Installation et Exécution**

### 📦 **Prérequis**
- [Docker](https://www.docker.com/) et [Docker Compose](https://docs.docker.com/compose/)
- **Python 3.8+** si vous exécutez sans Docker

### 🔧 **Lancer l'application avec Docker**
Dans le terminal, exécutez :
```bash
docker-compose up --build
```
Cela va :
- Construire et démarrer le **backend (FastAPI)** sur `http://localhost:8000`
- Construire et démarrer le **frontend (Streamlit)** sur `http://localhost:8501`

### 📂 **Arrêter les conteneurs**
```bash
docker-compose down
```

## 🎨 **Utilisation**
1. **Accédez à l'interface Streamlit** : [http://localhost:8501](http://localhost:8501)
2. **Chargez une image** (formats supportés : `.jpg`, `.jpeg`, `.png`)
3. **Choisissez une méthode d'analyse** :
   - **OpenCV** : Analyse du flou et du bruit dans l'image
   - **NIMA** : Évaluation du score de qualité de l'image
4. **Obtenez une analyse complète** avec des recommandations

## 🔍 **Développement**
Si vous souhaitez exécuter les services **manuellement** sans Docker :

### 1️⃣ **Démarrer le backend (FastAPI)**
```bash
cd backend/app
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2️⃣ **Démarrer le frontend (Streamlit)**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## ✨ **Améliorations possibles**
- 🧠 **Intégration de modèles d'intelligence artificielle avancés**
- 📊 **Ajout de graphiques et visualisations pour une meilleure interprétation**
- 🔍 **Amélioration des performances de traitement des images**
- 🛠️ **Déploiement sur un serveur cloud pour une utilisation en ligne**

## 📝 **Licence**
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

🚀 **Créé avec ❤️ par Jimmy** 🎉