# 🔧 GUIDE PRATIQUE - LANCER LE PROJET RAG

## 🚀 COMMENT RUN LE PROJET - ÉTAPE PAR ÉTAPE

### **ÉTAPE 1: INSTALLATION (10-15 minutes)**

```bash
# 1. Ouvrir un terminal et naviguer vers le projet
cd "C:\Users\HP\Desktop\Projet 2  Assistant Médical RAG avec LLMs"

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
venv\Scripts\activate

# 4. Installer les dépendances (C'EST LONG - 15-20 minutes)
pip install -r requirements.txt
```

### **ÉTAPE 2: LANCER LES SERVICES**

#### **Option A: Lancer le Pipeline RAG Simple**

```bash
# Terminal 1: Exécuter le pipeline RAG
python -m src.pipeline.pipeline
```

**Ce que ça fait:**
- Charge les documents médicaux
- Crée les chunks
- Génère les embeddings
- Sauvegarde dans ChromaDB

#### **Option B: Lancer l'API FastAPI**

```bash
# Terminal 2: Démarrer l'API
uvicorn src.api.main:app --reload
```

**Ce que ça fait:**
- Lance l'API sur http://localhost:8000
- Expose les endpoints RAG
- Enregistre les métriques Prometheus

#### **Option C: Lancer Streamlit (Interface)**

```bash
# Terminal 3: Démarrer l'interface utilisateur
streamlit run src/frontend/app.py
```

**Ce que ça fait:**
- Ouvre une interface web sur http://localhost:8501
- Permet de poser des questions médicales
- Affiche les résultats RAG

#### **Option D: Lancer MLflow Tracking**

```bash
# Terminal 4: Démarrer MLflow UI
mlflow ui
```

**Ce que ça fait:**
- Ouvre MLflow UI sur http://localhost:5000
- Affiche les expériences et runs
- Montre les métriques et params

---

## 🖥️ INTERFACES DISPONIBLES

### **1. Interface Streamlit (http://localhost:8501)**

**Comment y accéder:**
```bash
# Après avoir lancé streamlit
# Ouvrir votre navigateur web
http://localhost:8501
```

**Ce que vous voyez:**
- Zone de saisie pour questions médicales
- Bouton "Query" pour traiter la question
- Résultats des chunks récupérés
- Réponse contextuelle générée
- Métriques de performance

**Comment l'utiliser:**
1. Taper une question médicale ex: "Quels sont les symptômes du diabète ?"
2. Cliquer sur "Query" ou "Process"
3. Attendre 1-2 secondes
4. Voir les chunks pertinents avec scores de similarité
5. Lire la réponse contextuelle

### **2. Interface API FastAPI (http://localhost:8000)**

**Comment y accéder:**
```bash
# Après avoir lancé uvicorn
http://localhost:8000
```

**Endpoints disponibles:**
- **/** : Racine avec informations système
- **/api/health** : Health check du système
- **/api/query** : Query RAG (POST avec JSON)
- **/api/ingest** : Ingestion de documents
- **/api/stats** : Statistiques système
- **/metrics** : Métriques Prometheus

**Comment tester:**
```bash
# Test de query API
curl -X POST "http://localhost:8000/api/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"diabetes symptoms\",\"top_k\":5}"
```

### **3. Interface MLflow (http://localhost:5000)**

**Comment y accéder:**
```bash
# Après avoir lancé mlflow ui
http://localhost:5000
```

**Ce que vous voyez:**
- Liste des experiments (medical_rag_experiments)
- Liste des runs (baseline_tfidf, embedding_minilm, etc.)
- Params de chaque run
- Metrics de chaque run (MRR, retrieval_time, etc.)
- Artifacts sauvegardés

**Comment l'utiliser:**
1. Cliquer sur "medical_rag_experiments"
2. Cliquer sur un run spécifique
3. Voir les params et metrics
4. Comparer différents runs

### **4. Interface Grafana (http://localhost:3000)**

**Pour l'activer:**
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

**Ce que vous voyez:**
- Dashboards Prometheus
- Graphiques de métriques RAG en temps réel
- Latence de retrieval, nombre de requêtes, erreurs

---

## ⚠️ PROBLÈMES POSSIBLES ET SOLUTIONS

### **Problème 1: pip install prend trop de temps**

**Cause:**
- Téléchargement de modèles ML lourds (PyTorch, Transformers)

**Solution:**
```bash
# Soyez patient (15-20 minutes)
# OU installer seulement les packages essentiels:
pip install fastapi uvicorn langchain chromadb sentence-transformers
```

### **Problème 2: Streamlit ne s'ouvre pas**

**Cause:**
- Port 8501 déjà utilisé
- Streamlit pas installé

**Solution:**
```bash
# Vérifier l'installation
pip install streamlit

# Changer le port
streamlit run src/frontend/app.py --server.port 8502
```

### **Problème 3: MLflow ne montre pas de runs**

**Cause:**
- MLflow pas démarré
- Experiment pas créée

**Solution:**
```bash
# Créer manuellement l'expérience
python -c "
import mlflow
mlflow.set_experiment('medical_rag_experiments')
print('Experiment created')
"
```

### **Problème 4: API renvoie erreur 404**

**Cause:**
- API pas démarrée
- Mauvais endpoint

**Solution:**
```bash
# Vérifier que l'API tourne
curl http://localhost:8000/api/health

# Vérifier les endpoints disponibles
curl http://localhost:8000/
```

### **Problème 5: Documents médicaux non chargés**

**Cause:**
- Pas de fichiers dans data/raw/
- Path incorrect

**Solution:**
```bash
# Vérifier les documents
ls data/raw/

# Si vide, créer des documents de test
echo "Diabetes symptoms..." > data/raw/test_doc.txt

# Relancer le pipeline
python -m src.pipeline.pipeline
```

---

## 🎯 CE QUE FAIT LE PROJET CONCRÈTEMENT

### **Fonctionnement du Pipeline RAG:**

**1. INGESTION DES DOCUMENTS**
```
Documents médicaux (PDF/DOCX/TXT) → Chargement → Stockage
```
- Charge les fichiers médicaux depuis `data/raw/`
- Extrait le texte des PDF/DOCX
- Stocke pour traitement

**2. CHUNKING (SEGMENTATION)**
```
Document → Chunks de 1000 caractères avec overlap 200
```
- Divise les documents en segments gérables
- Conserve le contexte avec overlap
- Ex: "Diabetes Mellitus..." → Chunk 1, Chunk 2, etc.

**3. EMBEDDINGS (VECTORIZATION)**
```
Texte → Vecteurs numériques (384 dimensions)
```
- Transforme le texte en vecteurs sémantiques
- Utilise MiniLM-L6-v2
- Permet la recherche vectorielle

**4. RETRIEVAL (RECHERCHE)**
```
Question → Embedding → Recherche vectorielle → Chunks pertinents
```
- Transforme la question en embedding
- Cherche les chunks les plus similaires
- Classe par similarité (cosine similarity)

**5. RÉPONSE GÉNÉRÉE**
```
Chunks pertinents → Réponse contextuelle + Sources
```
- Génère une réponse basée sur les chunks
- Affiche les sources pour vérification
- Monte la traçabilité

---

## 💡 COMMENT UTILISER LE PROJET

### **Utilisation 1: Assistant Médical Personnel**

**Pour:**
- Trouver rapidement des informations médicales
- Obtenir des réponses sourcées
- Comparer différents traitements

**Comment:**
1. Ouvrir Streamlit (http://localhost:8501)
2. Poser une question: "Quels sont les symptômes du diabète ?"
3. Voir les 5 chunks les plus pertinents
4. Lire la réponse contextuelle

### **Utilisation 2: Recherche Documentaire**

**Pour:**
- Rechercher dans des documents médicaux
- Trouver des informations spécifiques
- Comparer différentes sources

**Comment:**
1. Préparer les documents dans `data/raw/`
2. Exécuter: `python -m src.pipeline.pipeline`
3. Poser des questions spécifiques
4. Voir les chunks récupérés

### **Utilisation 3: Comparaison de Modèles**

**Pour:**
- Tester différents modèles d'embeddings
- Comparer les performances
- Choisir le meilleur modèle

**Comment:**
1. Exécuter: `python -m src.models.embedding_comparator`
2. Voir les métriques de chaque modèle
3. Comparer MRR et latence
4. Choisir le meilleur modèle

### **Utilisation 4: Monitoring et Analyse**

**Pour:**
- Suivre les performances du système
- Détecter les erreurs
- Optimiser les temps de réponse

**Comment:**
1. Ouvrir MLflow (http://localhost:5000)
2. Voir les runs et métriques
3. Comparer différentes configurations
4. Identifier les problèmes

---

## 🎤 PRÉSENTATION - CE QUE MONTRER

### **Ce que vous devez présenter:**

**1. LE PROBLÈME (2 min)**
- Accès difficile à l'information médicale
- Recherche manuelle chronophage
- Besoin d'assistant IA contextuel

**2. LA SOLUTION RAG (1 min)**
- Pipeline: Documents → Embeddings → Retrieval → Réponses
- Technologies: LangChain, ChromaDB, MiniLM-L6-v2
- Avantages: Réponses sourcées, traçables

**3. LA DÉMO LIVE (3 min)**
- **IMPORTANT**: Montrer que ça fonctionne en direct
- Lancer Streamlit
- Poser une query médicale
- Montrer les résultats retrieval
- Expliquer ce qui se passe "behind the scenes"

**4. L'ARCHITECTURE (1 min)**
- Schéma du pipeline
- Composants techniques
- Pourquoi ces choix technologiques

**5. LES RÉSULTATS (1 min)**
- MRR = 1.000 (testing)
- Latence < 50ms
- 5+ modèles comparés
- Tests E2E passants

**6. LES AMÉLIORATIONS (1 min)**
- BioBERT spécialisé
- Support multi-modal
- Déploiement cloud

---

## 📋 CHECKLIST PRÉSENTATION

### **Avant (30 minutes):**
- [ ] Lancer API FastAPI (Terminal 1)
- [ ] Lancer Streamlit (Terminal 2)
- [ ] Lancer MLflow UI (Terminal 3)
- [ ] Vérifier que tous les services fonctionnent
- [ ] Préparer la query de test: "diabetes symptoms"
- [ ] Pratiquer la démo 3 fois

### **Pendant:**
- [ ] Parler clairement et avec enthousiasme
- [ ] Expliquer le pipeline RAG simplement
- [ ] Montrer les interfaces en direct
- [ ] Mettre en avant les résultats
- [ ] Être prêt pour les questions

### **Interface à montrer en priorité:**
1. **Streamlit** - L'interface utilisateur principale
2. **MLflow** - Pour montrer le tracking et les métriques
3. **API (optionnel)** - Pour montrer le backend technique

---

## 🚀 COMMANDE RAPIDE POUR LANCER TOUT

```bash
# Terminal 1: Pipeline RAG
python -m src.pipeline.pipeline

# Terminal 2: API FastAPI
uvicorn src.api.main:app --reload

# Terminal 3: Streamlit Interface
streamlit run src/frontend/app.py

# Terminal 4: MLflow Tracking
mlflow ui
```

**Puis ouvrir dans le navigateur:**
- Streamlit: http://localhost:8501
- MLflow: http://localhost:5000
- API: http://localhost:8000/docs

---

## 💡 CONSEILS PRATIQUES

1. **Utilisez 3+ terminaux** pour éviter les conflits
2. **Pratiquez la démo** avant présentation
3. **Ayez un plan backup** si Streamlit ne marche pas (utiliser API directement)
4. **Montrez les résultats concrets** (MRR, latence, chunks pertinents)
5. **Expliquez simplement** RAG pour le public non-technique

---

**🎉 VOILÀ ! Vous savez maintenant comment lancer le projet, voir les interfaces, et le présenter !**