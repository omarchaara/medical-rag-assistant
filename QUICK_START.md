# 🚀 QUICK START - COMMANDS ESSENTIELLES

## COMMANDES RAPIDES POUR L'ÉQUIPE

### 1. CLONER ET INSTALLER
```bash
git clone https://github.com/omarchaara/medical-rag-assistant.git
cd medical-rag-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. EXÉCUTER LE PIPELINE
```bash
# Pipeline RAG complet (Jour 2)
python -m src.pipeline.pipeline

# Baselines RAG (Jour 3)
python -m src.models.baseline

# Comparer embeddings (Jour 3)
python -m src.models.embedding_comparator
```

### 3. MLFLOW TRACKING
```bash
# Terminal 1 - Démarrer MLflow UI
mlflow ui

# Terminal 2 - Enregistrer des runs
python -c "import mlflow; mlflow.set_experiment('medical_rag_experiments'); with mlflow.start_run(): mlflow.log_metric('test', 0.95)"

# Ouvrir le navigateur
http://localhost:5000
```

### 4. DOCKER (Optionnel)
```bash
# Démarrer tous les services
docker-compose up -d

# Vérifier les services
docker-compose ps

# Arrêter
docker-compose down
```

### 5. TESTS
```bash
# Exécuter les tests
pytest

# Tests avec coverage
pytest --cov=src --cov-report=html
```

---

## 📚 DOCUMENTATION DÉTAILLÉE

- **TEAM_SETUP_GUIDE.md** - Guide d'installation complet
- **README_J2.md** - Guide Jour 2 (Data Pipeline)
- **README_J3.md** - Guide Jour 3 (Training Pipeline)
- **J3_RESULTS.md** - Résultats Jour 3

---

## 🔗 LIENS

- **GitHub**: https://github.com/omarchaara/medical-rag-assistant
- **MLflow UI**: http://localhost:5000
- **API (Docker)**: http://localhost:8000
- **Frontend (Docker)**: http://localhost:8501