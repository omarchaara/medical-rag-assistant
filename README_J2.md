# Jour 2 - RAG Medical Data Pipeline

## 🎯 Objectifs RAG Spécifiques

Ce Jour 2 est adapté spécifiquement pour un système **RAG (Retrieval-Augmented Generation) médical**, contrairement à un pipeline ETL classique.

### 🔄 Approche RAG vs ETL Classique

| Aspect | ETL Classique | Notre RAG Médical |
|--------|---------------|-------------------|
| **Données** | CSV, JSON, tabulaires | PDF, HTML, documents médicaux |
| **Traitement** | Pandas/Spark features | LangChain document chunking |
| **Features** | Numériques/catégorielles | Embeddings BioBERT (384 dims) |
| **Stockage** | PostgreSQL/MongoDB | ChromaDB (vectors) + PostgreSQL (metadata) |
| **EDA** | Histogrammes, corrélations | Analyse chunks, qualité embeddings |

---

## 🏗️ Architecture Pipeline RAG J2

```
DOCUMENTS MÉDICAUX
    ↓
DOCUMENT LOADER (LangChain)
    ↓
TEXT CHUNKING (512 tokens, overlap 50)
    ↓
MEDICAL CLEANING (termes, boundaries)
    ↓
EMBEDDING GENERATION (BioBERT)
    ↓
CHROMADB INDEXING (vectors)
    ↓
POSTGRESQL METADATA (filtres)
```

---

## 📁 Fichiers Créés

### **src/ingestion/medical_loader.py**
- `MedicalDocumentLoader` : Charge PDF, HTML, text
- Gestion automatique de sample data pour tests
- Logging détaillé des erreurs de parsing

### **src/processing/chunker.py**
- `MedicalTextChunker` : Chunking intelligent médical
- Classification des chunks (symptômes, traitement, etc.)
- Filtrage par qualité des chunks
- Fusion de chunks trop courts

### **src/processing/embeddings.py**
- `MedicalEmbeddingGenerator` : Embeddings sentence-transformers
- `BioBERTEmbeddingGenerator` : Spécialisé domaine médical
- Normalisation L2 des vecteurs
- Calcul de similarité cosinus

### **src/processing/chroma_indexer.py**
- `ChromaIndexer` : Indexation vectorielle
- Recherche sémantique (similarity search)
- Filtrage par metadata
- Export metadata pour tracking

### **src/processing/pipeline.py**
- `MedicalRAGPipeline` : Pipeline complet RAG
- Orchestration de tous les composants
- Statistiques détaillées du pipeline
- Test de queries pour validation

### **tests/test_rag_pipeline.py**
- Tests unitaires pour chaque composant
- Tests d'intégration pipeline complet
- Tests de qualité des données RAG

---

## 🚀 Comment Utiliser

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Exécuter la pipeline
```bash
cd "C:\Users\HP\Desktop\Projet 2  Assistant Médical RAG avec LLMs"
python -m src.processing.pipeline
```

### 3. Tester individuellement
```python
from src.ingestion.medical_loader import MedicalDocumentLoader
from src.processing.chunker import MedicalTextChunker
from src.processing.embeddings import MedicalEmbeddingGenerator
from src.processing.chroma_indexer import ChromaIndexer

# Charger documents
loader = MedicalDocumentLoader(data_dir="./data/raw")
documents = loader.load_sample_documents()

# Chunking
chunker = MedicalTextChunker()
chunks = chunker.chunk_documents(documents)

# Embeddings
embedder = MedicalEmbeddingGenerator()
embeddings = embedder.generate_document_embeddings(chunks)

# Indexation
indexer = ChromaIndexer()
indexer.index_documents(chunks, embeddings)
```

### 4. Exécuter les tests
```bash
pytest tests/test_rag_pipeline.py -v
```

---

## 📊 Métriques Pipeline

### Documents
- **Documents chargés** : N documents sources
- **Chunks générés** : N chunks après segmentation
- **Chunks filtrés** : N chunks après qualité

### Embeddings
- **Dimension** : 384 (all-MiniLM-L6-v2) ou 768 (BioBERT)
- **Normalisation** : L2 normalisée (norm = 1.0)
- **Temps génération** : ~100-500ms par document

### Indexation
- **Documents indexés** : N documents dans ChromaDB
- **Taille collection** : Size en MB
- **Performance query** : <100ms pour top_k=5

---

## 🔍 Contrôles Qualité RAG

### Tests Automatisés
- ✅ Aucun document vide
- ✅ Chunks dans range [50, 2000] caractères
- ✅ Metadata complets (chunk_id, chunk_index, etc.)
- ✅ Embeddings normalisés (norm ≈ 1.0)
- ✅ ChromaDB indexation réussie

### Validation Manuelle
- ✅ Cohérence des chunks (pas de coupures médicales incohérentes)
- ✅ Classification des types de chunks (symptômes, traitement, etc.)
- ✅ Qualité des embeddings (similarité sémantique testée)
- ✅ Performance de recherche (résultats pertinents)

---

## 📈 EDA RAG Spécifique

### Analyses recommandées :
1. **Distribution des tailles de chunks** : Histogramme des longueurs
2. **Types de chunks** : Distribution (symptômes, traitement, diagnostic)
3. **Qualité des embeddings** : Similarité cosinus, clustering
4. **Couverture thématique** : Diversité des sujets médicaux
5. **Metadata completeness** : % de chunks avec metadata complets

### Visualisations à créer :
- `length_distribution.png` : Histogramme des longueurs
- `chunk_type_distribution.png` : Bar plot des types
- `embedding_similarity_matrix.png` : Heatmap similarité
- `topic_coverage.png` : Couverture des sujets médicaux

---

## 🎯 Critères de Succès J2

✅ **Pipeline RAG implémentée** : Loading → Chunking → Embedding → Indexation
✅ **Documents chargés** : 10+ documents médicaux (sample data)
✅ **Chunks cohérents** : Pas de coupures médicales incohérentes
✅ **Embeddings générés** : BioBERT/sentence-transformers fonctionnels
✅ **ChromaDB indexé** : Documents recherchables
✅ **Tests passent** : 5+ tests qualité RAG
✅ **EDA réalisée** : Insights sur documents et embeddings
✅ **Dataset sauvegardé** : medical_chunks_v1.json + metadata

---

## 🔄 Prochaines Étapes (J3)

Une fois J2 terminé :
- **RAG Retrieval Chain** : LangChain retrieval complet
- **Query Processing** : Normalization, expansion
- **Context Building** : Assemblage intelligent des chunks
- **Performance Optimization** : Tuning top_k, similarity threshold

---

## 🐛 Résolution de Problèmes Communs

### Problème : Pas de documents dans data/raw
**Solution** : Le pipeline crée automatiquement des sample documents si le dossier est vide.

### Problème : Erreur modèle embedding
**Solution** : Utiliser "sentence-transformers/all-MiniLM-L6-v2" (plus léger) au lieu de BioBERT.

### Problème : ChromaDB timeout
**Solution** : Vérifier que le service ChromaDB n'est pas déjà occupé ou réduire le batch_size.

### Problème : Mémoire insuffisante
**Solution** : Réduire chunk_size à 256 ou traiter par batch plus petit.

---

## 📚 Références

- [LangChain Documentation](https://python.langchain.com/)
- [Sentence-Transformers](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Best Practices](https://www.deeplearning.ai/)

---

**Jour 2 RAG Adapté : Prêt pour ingestion de documents médicaux avec qualité RAG !** 🏥
