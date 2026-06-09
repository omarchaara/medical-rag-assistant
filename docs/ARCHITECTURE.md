# Architecture Medical RAG Assistant

## Vue d'ensemble

Système de question-réponse médical utilisant RAG (Retrieval-Augmented Generation) pour fournir des réponses basées sur la littérature scientifique et les guidelines cliniques.

```
+--------------------------------------------------------------+
¦                    SOURCES DE DONNÉES                       ¦
¦                                                              ¦
¦  • Articles PubMed                                           ¦
¦  • Guidelines OMS                                            ¦
¦  • Recommandations HAS                                       ¦
¦  • Fichiers PDF médicaux                                     ¦
¦  • APIs médicales                                            ¦
¦  • Kafka (flux futurs)                                       ¦
+--------------------------------------------------------------+
                        ¦
                        ?
+--------------------------------------------------------------+
¦                 INGESTION & NETTOYAGE                       ¦
¦                                                              ¦
¦  • FastAPI Upload API                                        ¦
¦  • Kafka Consumer                                            ¦
¦  • Extraction PDF                                            ¦
¦  • Nettoyage texte                                           ¦
¦  • Découpage (Chunking)                                      ¦
¦                                                              ¦
¦ Technologies :                                               ¦
¦ FastAPI, Kafka, LangChain Document Loaders                  ¦
+--------------------------------------------------------------+
                        ¦
                        ?
+--------------------------------------------------------------+
¦            TRAITEMENT & FEATURE ENGINEERING                 ¦
¦                                                              ¦
¦  • Prétraitement NLP                                         ¦
¦  • Chunk Optimization                                        ¦
¦  • Génération Embeddings                                     ¦
¦  • Métadonnées documentaires                                 ¦
¦                                                              ¦
¦ Technologies :                                               ¦
¦ Python, Pandas, PySpark, BioBERT                            ¦
+--------------------------------------------------------------+
                        ¦
                        ?
+--------------------------------------------------------------+
¦                STOCKAGE INTERMÉDIAIRE                       ¦
¦                                                              ¦
¦  PostgreSQL                                                  ¦
¦    • utilisateurs                                            ¦
¦    • historique requêtes                                     ¦
¦    • métadonnées documents                                   ¦
¦                                                              ¦
¦  ChromaDB / Milvus                                           ¦
¦    • embeddings vectoriels                                   ¦
¦                                                              ¦
¦  Redis                                                       ¦
¦    • cache réponses                                          ¦
¦                                                              ¦
¦  Parquet                                                     ¦
¦    • datasets préparés                                       ¦
+--------------------------------------------------------------+
                        ¦
                        ?
+--------------------------------------------------------------+
¦            MACHINE LEARNING & INFÉRENCE                     ¦
¦                                                              ¦
¦  Pipeline RAG                                                ¦
¦                                                              ¦
¦  Question utilisateur                                        ¦
¦          ?                                                   ¦
¦  Retrieval ChromaDB                                          ¦
¦          ?                                                   ¦
¦  Context Builder                                             ¦
¦          ?                                                   ¦
¦  LLM Mistral 7B via Ollama                                   ¦
¦          ?                                                   ¦
¦  Réponse avec citations                                      ¦
¦                                                              ¦
¦ Technologies :                                               ¦
¦ LangChain, Ollama, Mistral 7B, Llama 2                      ¦
¦ MLflow, FastAPI                                              ¦
+--------------------------------------------------------------+
                        ¦
                        ?
+--------------------------------------------------------------+
¦                VISUALISATION & API                          ¦
¦                                                              ¦
¦  Streamlit                                                   ¦
¦     • Chat médical                                           ¦
¦     • Upload PDF                                             ¦
¦     • Historique                                              ¦
¦                                                              ¦
¦  FastAPI                                                     ¦
¦     • /ask                                                   ¦
¦     • /ingest                                                ¦
¦     • /documents                                             ¦
¦                                                              ¦
¦  MLflow UI                                                   ¦
¦     • monitoring                                             ¦
¦     • expérimentations                                       ¦
¦                                                              ¦
+--------------------------------------------------------------+
```

## Stack Technologique

### 1. Ingestion & Traitement
- **LangChain** : Framework RAG standard industrie, orchestration pipeline
- **BioBERT/sentence-transformers** : Embeddings spécifiques domaine médical
- **PyPDF2/python-docx** : Parsing documents médicaux
- **Raison** : LangChain = écosystème le plus mature pour RAG, BioBERT = embeddings biomédicaux SOTA
- **Alternative écartée** : OpenAI embeddings (coût, privacy concerns pour données médicales)

### 2. Vector Database
- **ChromaDB** : Vector database open-source, Docker-native
- **Raison** : Léger, facile à déployer, bonne performance pour <1M documents
- **Alternative écartée** : Milvus (overkill pour MVP, setup complexe), Pinecone (SaaS payant)
- **Performance** : ~1000 QPS, latence <100ms pour similar search

### 3. LLM Inference
- **Ollama + Mistral 7B** : LLM open-source performant
- **Raison** : Mistral 7B = meilleur rapport qualité/ressources, Ollama = déploiement local simple
- **Baseline** : Qualité réponses comparable à GPT-3.5 pour domaine médical
- **Alternative écartée** : Llama 2 (moins performant), OpenAI API (coût, privacy)

### 4. Backend API
- **FastAPI** : Framework API moderne, async, documentation auto
- **Raison** : Performance élevée, typing Python, validation Pydantic
- **Alternative écartée** : Flask (moins performant, moins moderne)

### 5. Frontend
- **Streamlit** : Interface Python simple pour data apps
- **Raison** : Développement rapide, intégration native Python, idéal pour prototypes
- **Alternative écartée** : React/Next.js (surkill pour MVP, courbe d'apprentissage)

### 6. Metadata Storage
- **PostgreSQL** : Base de données relationnelle robuste
- **Raison** : Stockage queries, feedback, users, fiabilité production
- **Alternative écartée** : MongoDB (pas besoin schema-flexible pour ce use case)

### 7. Monitoring
- **MLflow** : Tracking expérimentations ML standard
- **Raison** : Industry standard pour MLOps, intégration LangChain
- **Alternative écartée** : Weights & Biases (SaaS payant), TensorBoard (ML spécifique)

### 8. Orchestration
- **Docker Compose** : Multi-service orchestration simple
- **Raison** : Setup local, développement collaboratif, production-ready
- **Alternative écartée** : Kubernetes (overkill pour 5 services)

## Flux de Données

### 1. Ingestion Pipeline
```
Medical Documents (PDF/DOCX) 
    ↓
LangChain Document Loader
    ↓
Text Splitter (chunk size=512, overlap=50)
    ↓
BioBERT Embeddings (sentence-transformers)
    ↓
ChromaDB Vector Store
    ↓
PostgreSQL Metadata Index
```

### 2. Query Pipeline
```
User Question (Streamlit UI)
    ↓
FastAPI POST /api/query
    ↓
LangChain Retrieval Chain
    ↓
ChromaDB Similarity Search (top_k=5)
    ↓
Context Building (retrieved chunks)
    ↓
Ollama Mistral 7B Generation
    ↓
Response Formatting (sources, confidence)
    ↓
Streamlit Display
```

## Services Docker (6 services)

### Service 1: chromadb
- **Role** : Vector database pour embeddings médicaux
- **Port** : 8001 (host) → 8000 (container)
- **Volume** : chroma_data (persistence)
- **Healthcheck** : /api/v1/heartbeat endpoint

### Service 2: postgres
- **Role** : Metadata storage (queries, documents, feedback)
- **Port** : 5432
- **Volume** : postgres_data
- **Database** : medical_rag_db
- **Healthcheck** : pg_isready command

### Service 3: ollama
- **Role** : LLM inference service (Mistral 7B)
- **Port** : 11434
- **Volume** : ollama_data (models cache)
- **GPU** : NVIDIA GPU support (optionnel)
- **Healthcheck** : /api/tags endpoint

### Service 4: api
- **Role** : FastAPI backend avec LangChain RAG
- **Port** : 8000
- **Dependencies** : chromadb, postgres, ollama
- **Healthcheck** : /api/health endpoint
- **Reload** : --reload pour développement

### Service 5: frontend
- **Role** : Streamlit UI pour professionnels médicaux
- **Port** : 8501
- **Dependencies** : api
- **Environment** : API_BASE_URL=http://api:8000

### Service 6: mlflow
- **Role** : Monitoring et tracking expérimentations
- **Port** : 5000
- **Volume** : mlflow_data (experiments, artifacts)
- **Storage** : SQLite backend

## Contraintes Respectées

### ✓ On-premise Only
- Tous services open-source, aucun cloud payant
- Ollama = LLM local, pas d'API externes
- ChromaDB = self-hosted vector DB

### ✓ Scalabilité
- Architecture microservices = scaling indépendant
- ChromaDB supporte millions de vectors
- PostgreSQL = horizontal scaling possible
- FastAPI async = high concurrency

### ✓ Monitoring Obligatoire
- MLflow pour tracking expérimentations
- Healthchecks sur tous services
- Logs structurés (loguru)
- Prometheus metrics endpoint (optionnel)

### ✓ Production-Ready
- Error handling complet
- Logging structuré
- Healthchecks
- Volumes persistents
- Environment variables configurables
- Documentation API auto (FastAPI docs)

## Ressources Système

### CPU
- **Minimum** : 4 cores
- **Recommandé** : 8 cores
- **Usage** : Embedding generation, document parsing

### RAM
- **Minimum** : 16GB
- **Optimal** : 32GB
- **Allocation** :
  - Ollama Mistral 7B : ~4-8GB
  - ChromaDB : ~2-4GB
  - PostgreSQL : ~1-2GB
  - API + Frontend : ~1-2GB

### Stockage
- **Minimum** : 50GB
- **Allocation** :
  - Ollama models : ~4GB
  - ChromaDB vectors : ~10-30GB (selon volume documents)
  - PostgreSQL : ~1-5GB
  - Documents source : ~10-20GB

### GPU
- **Optionnel** : NVIDIA GPU pour accélération Ollama
- **Bénéfice** : 2-5x plus rapide pour inference
- **Sans GPU** : CPU inference fonctionnel mais plus lent

## Alternatives Écartées

| Option | Raison Écartée |
|--------|----------------|
| Kafka pour ingestion | Overkill pour débits, Async suffisant |
| Milvus vs ChromaDB | Milvus = setup complexe, Chroma = Docker simple |
| OpenAI API | Coût, privacy, dépendance externe |
| Kubernetes | Docker Compose suffisant pour 6 services |
| React Frontend | Streamlit = développement 10x plus rapide |
| Pinecone Vector DB | SaaS payant, contrainte on-premise |
| MongoDB | Pas besoin flexibilité schema pour MVP |
| GPU obligatoire | CPU inference fonctionnel, accessibilité |

## Sécurité & Privacy

### Data Privacy
- Tous services local (aucun cloud)
- Pas d'envoi données médicales à APIs externes
- PostgreSQL encryption possible
- Environment variables pour secrets

### Authentication (Futur)
- JWT tokens avec python-jose
- Password hashing avec bcrypt
- Role-based access control (RBAC)

### API Security
- Rate limiting (Futur)
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy)

## Performance Cibles

### Latence
- **Query end-to-end** : <3 secondes (95th percentile)
- **Document ingestion** : <10 secondes par document
- **Vector search** : <100ms (top_k=5)

### Throughput
- **Concurrent queries** : 10+ simultanés
- **Document indexing** : 100+ documents/heure
- **API requests** : 100+ QPS

### Accuracy
- **Relevance precision** : >0.85 (top_k=5)
- **Answer quality** : >4/5 (feedback users)
- **Source attribution** : 100% (toujours afficher sources)

## Monitoring & Observability

### Logs
- **Format** : JSON structuré (loguru)
- **Niveaux** : DEBUG, INFO, WARNING, ERROR
- **Rotation** : 100MB per file, 7 days retention

### Metrics
- **MLflow** : Expérimentations, model versions
- **Prometheus** (optionnel) : System metrics, API latency
- **Custom metrics** : Query count, error rate, feedback score

### Alerts (Futur)
- Service down (healthcheck failure)
- High latency (>5s)
- Error rate >5%
- Storage >80% capacity

## Architecture Decision Records (ADR)

### ADR-001: Choix ChromaDB vs Milvus
**Date** : 2025-06-08
**Status** : Accepté
**Context** : Besoin vector database pour embeddings médicaux
**Décision** : ChromaDB
**Conséquences** :
- ✅ Setup Docker simple
- ✅ Performance suffisante pour MVP
- ❌ Scalability limitée vs Milvus
- ❌ Features avancées manquantes

### ADR-002: Choix Ollama vs OpenAI API
**Date** : 2025-06-08
**Status** : Accepté
**Context** : Besoin LLM pour génération réponses médicales
**Décision** : Ollama + Mistral 7B
**Conséquences** :
- ✅ Coût zéro (local)
- ✅ Privacy données médicales
- ✅ Contrôle complet modèle
- ❌ Setup plus complexe
- ❌ Performance moindre vs GPT-4

### ADR-003: Choix Streamlit vs React
**Date** : 2025-06-08
**Status** : Accepté
**Context** : Interface pour professionnels médicaux
**Décision** : Streamlit
**Conséquences** :
- ✅ Développement rapide
- ✅ Intégration Python native
- ❌ Personnalisation limitée
- ❌ Performance vs React

## Next Steps (Days 2-5)

### Day 2: Data Pipeline & Ingestion
- Implémenter document loaders (PDF, DOCX)
- Créer chunking strategy
- Intégrer BioBERT embeddings
- Tester ingestion pipeline avec documents sample

### Day 3: RAG Pipeline & Vector Search
- Implémenter LangChain retrieval chain
- Configurer ChromaDB vector store
- Tester semantic search
- Optimiser retrieval parameters (top_k, similarity threshold)

### Day 4: LLM Integration & API
- Configurer Ollama Mistral 7B
- Implémenter generation chain
- Créer FastAPI endpoints
- Tester end-to-end query pipeline

### Day 5: Frontend & Monitoring
- Développer Streamlit UI
- Intégrer MLflow tracking
- Ajouter feedback mechanism
- Démo finale & documentation

## Glossaire

- **RAG** : Retrieval-Augmented Generation - architecture combinant retrieval et generation
- **Embeddings** : Représentations vectorielles de texte pour similarité sémantique
- **Vector Database** : Base de données optimisée pour recherche similarity vectors
- **LLM** : Large Language Model - modèle de langage génératif
- **BioBERT** : BERT pre-trainé sur corpus biomedical
- **Mistral 7B** : LLM open-source 7 milliards de paramètres
- **LangChain** : Framework pour applications LLM
- **Ollama** : Tool pour运行 LLMs localement
