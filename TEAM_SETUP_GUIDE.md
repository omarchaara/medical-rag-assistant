# GUIDE D'INSTALLATION ET D'EXÉCUTION - PROJET RAG MÉDICAL

## 🚀 INSTRUCTIONS POUR L'ÉQUIPE

Ce guide contient toutes les commandes nécessaires pour cloner, installer et exécuter le projet Medical RAG Assistant.

---

## 📋 PRÉREQUIS

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.11+** (recommandé: 3.12)
- **Git** (pour cloner le repository)
- **Docker Desktop** (optionnel, pour déploiement en conteneurs)
- **7GB+ RAM** (pour les modèles ML)
- **10GB+ disque** (pour les dépendances et modèles)

---

## 🔧 ÉTAPE 1: CLONER LE PROJET

### Commandes Git

```bash
# Cloner le repository
git clone https://github.com/omarchaara/medical-rag-assistant.git

# Se déplacer dans le répertoire
cd medical-rag-assistant
```

### Vérification

```bash
# Vérifier la branche
git branch  # Doit afficher 'main'

# Vérifier le dernier commit
git log --oneline -1  # Doit afficher '19ef59a' ou récent
```

---

## 🐍 ÉTAPE 2: ENVIRONNEMENT PYTHON

### Option A: Utiliser venv (recommandé)

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Activer l'environnement (Mac/Linux)
source venv/bin/activate
```

### Option B: Utiliser conda

```bash
# Créer un environnement conda
conda create -n medical-rag python=3.12 -y

# Activer l'environnement
conda activate medical-rag
```

---

## 📦 ÉTAPE 3: INSTALLER LES DÉPENDANCES

### Commande d'installation

```bash
# Installer toutes les dépendances
pip install -r requirements.txt
```

### Note importante
- Cette installation peut prendre **15-20 minutes** (dépendances ML lourdes)
- Elle téléchargera **PyTorch, Transformers, Sentence-Transformers** (~2GB)
- Soyez patient pendant le téléchargement

### Vérification

```bash
# Vérifier les packages clés
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import sentence_transformers; print(f'Sentence-Transformers: OK')"
python -c "import mlflow; print(f'MLflow: OK')"
```

---

## 🏗️ ÉTAPE 4: STRUCTURE DU PROJET

### Arborescence

```
medical-rag-assistant/
├── data/
│   ├── raw/                  # Documents médicaux bruts
│   └── processed/            # Données traitées
├── src/
│   ├── ingestion/            # Chargement des documents
│   ├── processing/           # Chunking et embeddings
│   ├── models/               # Modèles RAG et training
│   ├── api/                  # API FastAPI
│   └── frontend/             # Interface Streamlit
├── docs/                     # Documentation
├── docker-compose.yml        # Configuration Docker
├── requirements.txt          # Dépendances Python
└── README_J3.md             # Guide Jour 3
```

---

## 🎯 ÉTAPE 5: EXÉCUTER LE PROJET

### Option A: Exécution locale (recommandée pour développement)

#### 1. Tester le Pipeline Jour 2

```bash
# Exécuter le pipeline RAG complet
python -m src.pipeline.pipeline

# Résultat attendu:
# - Chargement des documents médicaux
# - Chunking des documents
# - Génération des embeddings
# - Validation de la qualité des données
# - Tests de qualité (5/5 tests passants)
```

#### 2. Tester les Baselines Jour 3

```bash
# Exécuter les baselines RAG
python -m src.models.baseline

# Résultat attendu:
# BASELINE RAG COMPARISON:
# TF-IDF Baseline MRR: 1.000
# Random Baseline MRR: 1.000
```

#### 3. Tester les Embeddings Jour 3

```bash
# Comparer les modèles d'embedding
python -m src.models.embedding_comparator

# Résultat attendu:
# EMBEDDING MODEL COMPARISON:
# MiniLM-L6-v2: 384 dims, MRR=1.000
```

#### 4. Exécuter MLflow Tracking

```bash
# Démarrer MLflow UI (dans un terminal séparé)
mlflow ui

# Laissez ce terminal ouvert
# UI accessible sur: http://localhost:5000
```

#### 5. Enregistrer des runs MLflow

```bash
# Dans un autre terminal
python -c "
import mlflow
mlflow.set_experiment('medical_rag_experiments')
with mlflow.start_run(run_name='test_run'):
    mlflow.log_param('test_param', 'test_value')
    mlflow.log_metric('test_metric', 0.95)
    print('Run enregistré avec succès')
"
```

### Option B: Exécution Docker (recommandée pour production)

#### 1. Démarrer tous les services

```bash
# Démarrer tous les conteneurs
docker-compose up -d

# Vérifier les services
docker-compose ps
```

#### 2. Services disponibles

- **API FastAPI**: http://localhost:8000
- **Frontend Streamlit**: http://localhost:8501
- **PostgreSQL**: localhost:5432
- **ChromaDB**: localhost:8001

#### 3. Arrêter les services

```bash
# Arrêter tous les conteneurs
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

---

## 📊 ÉTAPE 6: VÉRIFIER LES RÉSULTATS

### Vérifier MLflow UI

```bash
# Ouvrir le navigateur sur
http://localhost:5000

# Vous devriez voir:
# - Experiment: medical_rag_experiments
# - Runs: baseline_tfidf, baseline_random, embedding_minilm
# - Params et metrics pour chaque run
```

### Vérifier les fichiers générés

```bash
# Vérifier les données traitées
ls data/processed/

# Vérifier les métriques
cat J3_RESULTS.md
```

---

## 🧪 ÉTAPE 7: TESTS

### Exécuter les tests unitaires

```bash
# Exécuter tous les tests
pytest

# Exécuter avec coverage
pytest --cov=src --cov-report=html
```

### Vérifier la qualité des données

```bash
# Exécuter les tests de qualité
python -m src.pipeline.quality_tests
```

---

## 🔍 ÉTAPE 8: DÉPANNAGE

### Problèmes courants

#### 1. Erreur "pypdf not found"
```bash
pip install pypdf
```

#### 2. Erreur MLflow "experiment does not exist"
```bash
# L'expérience sera créée automatiquement au premier run
# Pas besoin de création manuelle
```

#### 3. Erreur Docker "port already in use"
```bash
# Changer les ports dans docker-compose.yml
# Ou arrêter les services qui utilisent ces ports
```

#### 4. PyTorch installation lente
```bash
# Soyez patient, cela prend du temps
# OU utiliser une version précompilée:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Logs et debugging

```bash
# Vérifier les logs
ls logs/

# Activer le logging détaillé
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

---

## 🚀 ÉTAPE 9: DÉPLOIEMENT EN PRODUCTION

### Configuration production

```bash
# Copier les variables d'environnement
cp .env.example .env

# Modifier .env avec vos configurations
vim .env
```

### Démarrer production

```bash
# Démarrer avec Docker Compose
docker-compose -f docker-compose.yml up -d

# Vérifier les services
docker-compose ps
```

---

## 📚 DOCUMENTATION SUPPLÉMENTAIRE

### Guides disponibles

- **README_J2.md** - Guide Jour 2 (Data Pipeline)
- **README_J3.md** - Guide Jour 3 (Training Pipeline)
- **J3_RESULTS.md** - Résultats détaillés Jour 3
- **docs/ARCHITECTURE.md** - Architecture technique
- **docs/JOUR2_RAG_ADAPTED.md** - Adaptation RAG Jour 2
- **docs/JOUR3_RAG_ADAPTED.md** - Adaptation RAG Jour 3

---

## 🤝 SUPPORT

### Pour obtenir de l'aide

1. Vérifier les logs dans le dossier `logs/`
2. Consulter la documentation dans `docs/`
3. Vérifier MLflow UI pour les résultats d'exécution
4. Contactez l'équipe de développement

### Commandes utiles

```bash
# Vérifier l'état git
git status

# Mettre à jour le projet
git pull origin main

# Vérifier les branches
git branch -a

# Nettoyer l'environnement
pip freeze > requirements_backup.txt
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## ✅ CHECKLIST DE VALIDATION

Avant de considérer l'installation comme terminée :

- [ ] Git clone réussi
- [ ] Environnement Python créé et activé
- [ ] Dépendances installées sans erreur
- [ ] Pipeline Jour 2 exécuté avec succès
- [ ] Baselines Jour 3 exécutées avec succès
- [ ] Embeddings Jour 3 testés avec succès
- [ ] MLflow UI accessible sur localhost:5000
- [ ] Runs MLflow visibles dans l'interface
- [ ] Tests unitaires passants
- [ ] Documentation consultée

---

## 🎯 RESUME RAPIDE

### Commandes essentielles

```bash
# Installation complète
git clone https://github.com/omarchaara/medical-rag-assistant.git
cd medical-rag-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Exécution rapide
python -m src.pipeline.pipeline
python -m src.models.baseline
python -m src.models.embedding_comparator

# MLflow
mlflow ui  # Terminal 1
python -c "import mlflow; mlflow.set_experiment('medical_rag_experiments'); with mlflow.start_run(): mlflow.log_metric('test', 0.95)"  # Terminal 2

# Docker
docker-compose up -d
docker-compose down
```

---

## 📞 CONTACT

- **Repository**: https://github.com/omarchaara/medical-rag-assistant
- **Documentation**: Voir dossier `docs/`
- **Issues**: GitHub Issues du repository

---

**Bonne installation et bon développement !** 🚀🏥