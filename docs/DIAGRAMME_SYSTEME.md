# Diagramme du Système - Medical RAG Assistant

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────────┐
│                     UTILISATEURS FINAUX                              │
│  (Médecins, Infirmiers, Étudiants en Médecine)                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STREAMLIT FRONTEND                              │
│  Interface Web / Questions / Réponses / Feedback                    │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP REST API
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                               │
│  • POST /api/query      → Question utilisateur                      │
│  • POST /api/ingest     → Ingestion documents                       │
│  • GET  /api/health     → Health check                              │
└────────┬──────────────────────────┬─────────────────────────────────┘
         │                          │
         │ LangChain RAG Chain      │ PostgreSQL (Metadata)
         ▼                          ▼
┌─────────────────────┐    ┌──────────────────────────────────────┐
│   CHROMA VECTOR DB  │    │  • Queries history                  │
│  • Medical embeddings│    │  • Documents metadata               │
│  • Semantic search  │    │  • User feedback                    │
│  • top_k=5 retrieval│    │  • Analytics data                   │
└──────────┬──────────┘    └──────────────────────────────────────┘
           │
           │ LangChain Retrieval
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OLLAMA LLM SERVICE                              │
│  • Mistral 7B Model                                                 │
│  • Context Generation                                               │
│  • Answer Production                                                │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Pipeline d'Ingestion

```
┌─────────────────────────────────────────────────────────────────────┐
│                   SOURCES DE DONNÉES                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │  PubMed  │  │  NIH     │  │   WHO    │  │   HAS    │          │
│  │  Central │  │  Guidelines│ │ Guidelines│ │  Guides  │          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘          │
└───────┼─────────────┼─────────────┼─────────────┼──────────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT LOADER                                   │
│  • PDF Parsing (PyPDF2)                                             │
│  • DOCX Parsing (python-docx)                                       │
│  • HTML Parsing (BeautifulSoup)                                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TEXT CHUNKING                                     │
│  • Chunk size: 512 tokens                                           │
│  • Overlap: 50 tokens                                               │
│  • Boundary respect (paragraphes, phrases)                           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 EMBEDDING GENERATION                                 │
│  • BioBERT / sentence-transformers                                   │
│  • Medical domain-specific embeddings                                │
│  • Vector dimension: 384/768                                        │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 CHROMA INDEXATION                                   │
│  • Store vectors with metadata                                      │
│  • Create collections by document type                              │
│  • PostgreSQL sync for metadata search                              │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎯 Pipeline de Requête (Runtime)

```
┌─────────────────────────────────────────────────────────────────────┐
│                 QUESTION UTILISATEUR                                │
│  "Quels sont les symptômes de l'infarctus du myocarde ?"            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              QUERY PREPROCESSING                                     │
│  • Normalization (lowercase, accents)                               │
│  • Medical term detection (optionnel)                               │
│  • Query expansion (synonyms médicaux)                              │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              QUERY EMBEDDING                                        │
│  • Generate embedding vector for question                          │
│  • Same model as documents (BioBERT)                                │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              SEMANTIC SEARCH (ChromaDB)                             │
│  • Cosine similarity search                                         │
│  • top_k=5 most relevant chunks                                    │
│  • Score threshold: 0.75 (configurable)                            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              CONTEXT BUILDING                                      │
│  • Concatenate retrieved chunks                                    │
│  • Add source metadata                                              │
│  • Format for LLM prompt                                           │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PROMPT ENGINEERING                                     │
│                                                                      │
│  "Tu es un assistant médical professionnel. Basé sur le contexte     │
│   scientifique suivant, réponds à la question de manière précise    │
│   et cite toujours tes sources."                                    │
│                                                                      │
│  CONTEXTE: [retrieved chunks]                                       │
│  QUESTION: [user question]                                          │
│  SOURCES: [citation format]                                          │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              LLM GENERATION (Ollama + Mistral 7B)                   │
│  • Generate answer based on context                                 │
│  • Include citations in response                                    │
│  • Confidence estimation                                            │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              RESPONSE FORMATTING                                    │
│  {                                                                  │
│    "answer": "Texte de la réponse...",                              │
│    "sources": [                                                      │
│      {"title": "...", "authors": [...], "confidence": 0.85}        │
│    ],                                                               │
│    "confidence_score": 0.82,                                         │
│    "query_time_ms": 2450                                             │
│  }                                                                  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              LOGGING & MONITORING                                   │
│  • Log query, response, time to PostgreSQL                          │
│  • Track metrics in MLflow                                         │
│  • Store user feedback                                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              USER DISPLAY (Streamlit)                               │
│  • Show answer in readable format                                   │
│  • Display sources with links                                       │
│  • Show confidence score                                            │
│  • Feedback buttons (1-5 stars)                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 📊 Flux de Données Métadata

```
┌─────────────────────────────────────────────────────────────────────┐
│              POSTGRESQL SCHEMA                                       │
│                                                                      │
│  ┌─────────────────┐     ┌──────────────────┐                     │
│  │    users        │────▶│     queries      │                     │
│  │  • id           │     │  • id            │                     │
│  │  • username     │     │  • user_id       │                     │
│  │  • email        │     │  • question      │                     │
│  │  • created_at   │     │  • answer        │                     │
│  └─────────────────┘     │  • sources[]     │                     │
│                          │  • confidence    │                     │
│  ┌─────────────────┐     │  • created_at    │                     │
│  │   documents    │────▶└──────────────────┘                     │
│  │  • id          │                                                 │
│  │  • title       │     ┌──────────────────┐                     │
│  │  • file_path   │────▶│     feedback     │                     │
│  │  • doc_type    │     │  • id            │                     │
│  │  • chunk_count │     │  • query_id      │                     │
│  │  • indexed     │     │  • rating        │                     │
│  └─────────────────┘     │  • comment       │                     │
│                          │  • created_at    │                     │
│                          └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Workflow Collboratif (Git)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GITHUB WORKFLOW                                  │
│                                                                      │
│  ┌─────────┐    ┌──────────┐    ┌───────────┐    ┌─────────────┐  │
│  │  main   │───▶│ develop  │───▶│ feature/* │───▶│ Pull Request│  │
│  │ (stable)│    │ (integration)│ (dev)   │    │   (review)   │  │
│  └─────────┘    └──────────┘    └───────────┘    └─────────────┘  │
│       ▲                                    │                      │
│       │                                    ▼                      │
│       │                           ┌──────────────┐                │
│       └───────────────────────────│   Squash      │                │
│                                    │   Merge       │                │
│                                    └──────────────┘                │
└─────────────────────────────────────────────────────────────────────┘

Branches Types:
  • main          → Production stable
  • develop       → Integration (optionnel)
  • feature/*     → Nouvelles fonctionnalités
  • bugfix/*      → Corrections de bugs
  • hotfix/*      → Corrections urgentes
```

## 🐳 Docker Services

```
┌─────────────────────────────────────────────────────────────────────┐
│              DOCKER COMPOSE ARCHITECTURE                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  HOST MACHINE                                                  │  │
│  │  • Docker Engine                                               │  │
│  │  • Docker Compose                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                           │
│         │ docker-compose up                                         │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  DOCKER NETWORK: medical_rag_network                         │  │
│  │  172.20.0.0/16 bridge                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                                                           │
│         ├─── postgres:172.20.0.2:5432                              │
│         ├─── chromadb:172.20.0.3:8001                              │
│         ├─── api:172.20.0.4:8000                                   │
│         ├─── frontend:172.20.0.5:8501                              │
│         ├─── ollama:172.20.0.6:11434 (Day 4)                     │
│         └─── mlflow:172.20.0.7:5000 (Day 5)                       │
│                                                                     │
│  Volumes:                                                           │
│  • postgres_data → /var/lib/postgresql/data                        │
│  • chroma_data → /chroma/chroma                                     │
│  • ollama_data → /root/.ollama                                     │
│  • mlflow_data → /mlflow                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## 📈 Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────────────┐
│              MONITORING STACK                                      │
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │   LOGURU     │    │   MLFLOW      │    │  PROMETHEUS   │        │
│  │ Structured   │────▶ Experiment   │────▶ Metrics      │        │
│  │ Logging      │    │ Tracking      │    │ Collection   │        │
│  └──────────────┘    └──────────────┘    └──────────────┘        │
│         │                  │                  │                     │
│         │                  │                  ▼                     │
│         │                  │         ┌──────────────┐             │
│         │                  │         │ GRAFANA      │             │
│         │                  │         │ Dashboards   │             │
│         │                  │         └──────────────┘             │
│         ▼                  │                                        │
│  ┌──────────────┐         │                                        │
│  │  LOG FILES   │         │                                        │
│  │  /var/log/   │         │                                        │
│  └──────────────┘         │                                        │
│                           │                                        │
│                           ▼                                        │
│                  ┌──────────────┐                                 │
│                  │  HEALTH      │                                 │
│                  │  CHECKS      │                                 │
│                  │  /api/health │                                 │
│                  └──────────────┘                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

*Ces diagrammes illustrent l'architecture complète du système Medical RAG Assistant*
