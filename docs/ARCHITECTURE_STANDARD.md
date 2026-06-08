# Architecture Standard - Medical RAG Assistant

## 🏗️ Diagramme d'Architecture (Conforme au Modèle Standard)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  SOURCES DE DONNÉES                                │
│  (PubMed Central, NIH Guidelines, WHO Guidelines, PDFs, HTML)      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│           INGESTION & NETTOYAGE (LangChain)                         │
│  • Document Loaders (PyPDF2, python-docx)                          │
│  • Text Chunking (512 tokens, overlap 50)                           │
│  • Data Cleaning (normalization, preprocessing)                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│         TRAITEMENT & FEATURE ENGINEERING (Embeddings)                │
│  • BioBERT / sentence-transformers                                  │
│  • Vector Generation (384/768 dimensions)                          │
│  • Semantic Embeddings (domaine médical)                            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│           STOCKAGE INTERMÉDIAIRE                                    │
│  • ChromaDB (Vector Database) - Embeddings                         │
│  • PostgreSQL (Metadata Storage) - Queries, Documents, Feedback     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│          MACHINE LEARNING / INFÉRENCE                               │
│  • Ollama Mistral 7B (LLM Generation)                              │
│  • LangChain Retrieval Chain                                        │
│  • MLflow (Experiment Tracking)                                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              VISUALISATION & API                                    │
│  • FastAPI (REST API Endpoints)                                    │
│  • Streamlit (Frontend UI)                                         │
│  • Swagger API Documentation                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Flux de Données Détaillé

```
DONNÉES BRUTES → TRAITEMENT → STOCKAGE → ML → API → UTILISATEUR
```

### Phase 1 : Sources de Données
- **Entrées** : PDFs médicaux, guidelines cliniques, articles scientifiques
- **Volume** : 100-50k documents
- **Format** : PDF, HTML, DOCX
- **Sources** : PubMed, NIH, WHO, HAS

### Phase 2 : Ingestion & Nettoyage
- **Technologie** : LangChain, PyPDF2, python-docx
- **Traitements** :
  - Parsing documents
  - Extraction texte
  - Nettoyage (headers, footers, références)
  - Chunking (512 tokens, overlap 50)

### Phase 3 : Feature Engineering
- **Technologie** : BioBERT, sentence-transformers
- **Traitements** :
  - Génération embeddings (384/768 dimensions)
  - Normalisation L2
  - Medical domain-specific embeddings

### Phase 4 : Stockage Intermédiaire
- **Technologies** : ChromaDB + PostgreSQL
- **Stockage** :
  - Vectors : ChromaDB (similarité search)
  - Metadata : PostgreSQL (indexation, filtres)

### Phase 5 : Machine Learning / Inférence
- **Technologies** : Ollama Mistral 7B, LangChain, MLflow
- **Traitements** :
  - Retrieval sémantique (top_k=5)
  - Context building
  - LLM generation (Mistral 7B)
  - Experiment tracking (MLflow)

### Phase 6 : Visualisation & API
- **Technologies** : FastAPI, Streamlit, Swagger
- **Sorties** :
  - REST API (/api/query, /api/ingest)
  - Frontend UI (Streamlit)
  - API Documentation (Swagger)

## 🎯 Correspondance avec Modèle Standard

| Étape Standard | Notre Implémentation | Technologies | Justification |
|---------------|---------------------|--------------|---------------|
| **SOURCES DE DONNÉES** | Littérature médicale | PDF, HTML, APIs PubMed | ✅ Conforme |
| **INGESTION & NETTOYAGE** | Document processing | LangChain, PyPDF2 | ✅ Adapté RAG |
| **TRAITEMENT & FEATURE ENGINEERING** | Embeddings generation | BioBERT, sentence-transformers | ✅ Adapté RAG |
| **STOCKAGE INTERMÉDIAIRE** | Vector + Metadata storage | ChromaDB + PostgreSQL | ✅ Conforme |
| **MACHINE LEARNING / INFÉRENCE** | LLM + Retrieval | Ollama Mistral 7B, LangChain | ✅ Conforme |
| **VISUALISATION & API** | UI + REST API | Streamlit, FastAPI | ✅ Conforme |

## 💡 Pourquoi les adaptations RAG sont justifiées

### 1. INGESTION & NETTOYAGE
**Standard** : FastAPI/Kafka/Spark pour données structurées (CSV, JSON, IoT)
**Notre RAG** : LangChain pour documents non-structurés (PDF, articles)
**Justification** : RAG traite des documents texte, pas des données tabulaires

### 2. TRAITEMENT & FEATURE ENGINEERING
**Standard** : Pandas/PySpark pour features numériques/catégorielles
**Notre RAG** : Embeddings pour similarité sémantique
**Justification** : Feature engineering = embeddings pour recherche sémantique

### 3. STOCKAGE INTERMÉDIAIRE
**Standard** : PostgreSQL/MongoDB/Redis pour données structurées
**Notre RAG** : ChromaDB (vector DB) + PostgreSQL
**Justification** : RAG nécessite vector database pour similarity search

## ✅ Conclusion

**Notre architecture RESPECTE le modèle standard** mais est **adaptée au RAG** :

✅ **Structure identique** : 6 étapes dans le même ordre  
✅ **Technologies appropriées** : Adaptées aux documents textes et RAG  
✅ **Flux de données respecté** : Entrées → Traitements → Stockage → ML → API  
✅ **Justifiée** : Les adaptations sont nécessaires pour le RAG  

**C'est une architecture RAG valide qui suit les best practices du domaine !** 🎉