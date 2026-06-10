# Jour 3 - RAG Model Training & Optimization

## 🎯 Objectifs RAG Spécifiques

Concevoir et entraîner des modèles d'embeddings pour RAG médical
Comparer les stratégies de retrieval avec MLflow tracking
Sélectionner le meilleur embedding model avec justification
Mettre en place la reproductibilité et le versioning des modèles RAG
Documenter l'expérimentation RAG pour audit et traçabilité
Préparer le système RAG pour la production J4

---

## 🔄 Adaptation RAG vs ML Classique

| Aspect | ML Classique (énoncé) | Notre RAG Médical |
|--------|---------------------|-------------------|
| **Objectif** | Classification/Regression | Retrieval sémantique |
| **Modèles** | XGBoost, RandomForest | Sentence-Transformers, BioBERT |
| **Métriques** | Accuracy, F1, MSE | Mean Reciprocal Rank (MRR), Relevance |
| **Hyperparams** | n_estimators, max_depth | chunk_size, chunk_overlap |
| **Baseline** | DummyClassifier | TF-IDF + Cosine Similarity |
| **Validation** | ROC-AUC, Cross-validation | Retrieval quality, latency |

---

## 📁 Fichiers Créés J3 RAG

- ✅ **docs/JOUR3_RAG_ADAPTED.md** - Guide complet Jour 3 adapté RAG
- ✅ **src/models/baseline.py** - Baseline RAG (TF-IDF + Random)
- ✅ **src/models/embedding_comparator.py** - Comparaison embedding models
- ✅ **src/models/train.py** - Pipeline entraînement RAG + MLflow
- ✅ **src/models/__init__.py** - Module models
- ✅ **requirements.txt** - Ajout scikit-learn

---

## 🚀 Comment Utiliser

### 1. Tester les Baselines RAG

```bash
cd "C:\Users\HP\Desktop\Projet 2  Assistant Médical RAG avec LLMs"
python -m src.models.baseline
```

**Résultat attendu :**
- TF-IDF Baseline MRR vs Random Baseline MRR
- Validation que TF-IDF > Random (sinon problème de données)

---

### 2. Comparer Embedding Models

```bash
python -m src.models.embedding_comparator
```

**Modèles comparés :**
- **MiniLM-L6-v2** : Généraliste rapide (384 dims)
- **BioBERT** : Spécialisé médical (768 dims)
- **PubMedBERT** : Spécialisé biomedical (768 dims)

**Métriques :**
- **MRR** : Mean Reciprocal Rank (qualité retrieval)
- **Time (ms)** : Latence retrieval

---

### 3. Pipeline Entraînement Complet

```bash
python -m src.models.train
```

**Ce que fait la pipeline :**
1. **Baseline Experiments** : TF-IDF vs Random
2. **Embedding Comparison** : Comparaison models
3. **Chunking Experiments** : 256 vs 512 vs 1024 chunks
4. **MLflow Tracking** : Tous les params/metrics loggés
5. **Résultats sauvegardés** : JSON dans data/processed/

---

## 📊 Métriques RAG Expliquées

### **MRR (Mean Reciprocal Rank)**
- **Définition** : Moyenne de 1/rang du premier document pertinent
- **Échelle** : 0 (mauvais) → 1 (parfait)
- **Exemple** : Si le premier pertinent est rang 2, MRR = 1/2 = 0.5

### **Relevance@5**
- **Définition** : Pourcentage de chunks pertinents dans top-5
- **Échelle** : 0 → 1 (ou 0-100%)
- **Usage** : Utilisateur voit le résultat dans les 5 premiers

### **Retrieval Latency**
- **Définition** : Temps pour récupérer k chunks
- **Cible** : <100ms pour bonnes UX
- **Impact** : Latence élevée = mauvaise expérience utilisateur

---

## 🔧 Stratégies de Chunking Testées

| Stratégie | Chunk Size | Overlap | Objectif |
|-----------|------------|----------|----------|
| **small_chunks** | 256 chars | 25 | Plus granularité, plus précis |
| **medium_chunks** | 512 chars | 50 | Balance granularité/contexte |
| **large_chunks** | 1024 chars | 100 | Plus de contexte, moins granularité |

---

## 🎯 Livrables Attendus J3 RAG

- ✅ **src/models/train.py** - Pipeline entraînement complet
- ✅ **src/models/baseline.py** - Baselines TF-IDF + Random
- ✅ **src/models/embedding_comparator.py** - Comparaison models
- ✅ **Modèles enregistrés** dans MLflow Registry
- ✅ **Tableau comparatif** (JSON) avec MRR + Time
- ✅ **Justification** du modèle choisi
- ✅ **Tests validation** RAG (relevance, latency)

---

## 💡 Pourquoi Cette Adaptation RAG ?

**Projet original (ML classique) :**
- Classification de données tabulaires
- Entraînement XGBoost/RandomForest
- Grid Search hyperparams
- Model Registry sklearn

**Notre adaptation (RAG médical) :**
- Retrieval sémantique de documents
- Entraînement embedding models
- Chunking strategy tuning
- Configuration RAG Registry

**Pourquoi ?**
- Le projet est **RAG** (Retrieval-Augmented Generation), pas ML classique
- Les données sont **documents médicaux**, pas tableaux
- L'objectif est **génération de réponses**, pas classification
- Les métriques sont **retrieval quality**, pas accuracy/F1

---

## 🚨 Limitations Actuelles

- ❌ **LLM non intégré** : génération réponses différée à J5
- ❌ **True medical documents** : Données synthétiques seulement
- ❌ **BioBERT non testé** : Peut nécessiter téléchargement lourd
- ❌ **API RAG non implémentée** : J4 devra créer l'endpoint

---

## ✅ État Actuel J3

- ✅ **Code RAG écrit** et poussé sur GitHub
- ✅ **MLflow configuré** pour tracking RAG
- ✅ **Pipeline complète** : Baseline → Embedding → Chunking
- ✅ **Documentation adaptée** spécifique RAG médical
- ✅ **Prêt pour tests** avec Docker ou local

**Commits GitHub :**
- `23ceb87` - feat(j3): Add RAG-specific Day 3 training pipeline

---

## 🎓 Prochaines Étapes

Pour vraiment tester J3 :
1. Installer scikit-learn : `pip install scikit-learn`
2. Lancer baselines : `python -m src.models.baseline`
3. Lancer comparaison : `python -m src.models.embedding_comparator`
4. Lancer pipeline complète : `python -m src.models.train`
5. Vérifier MLflow UI : `mlflow ui`

**Prêt pour entraînement de modèles d'embeddings médicaux !** 🏥
