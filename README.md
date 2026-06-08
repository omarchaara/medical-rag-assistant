# Medical RAG Assistant with LLMs

A Retrieval-Augmented Generation (RAG) system for medical question-answering using scientific literature and clinical guidelines.

## Project Overview

This system provides accurate, evidence-based medical responses by:
- Indexing medical literature and clinical guidelines
- Using semantic search with BioBERT embeddings
- Generating answers with Mistral 7B via Ollama
- Providing a user-friendly interface for medical professionals

## Technology Stack

- **RAG Framework**: LangChain
- **LLM**: Mistral 7B (via Ollama)
- **Embeddings**: BioBERT (medical domain-specific)
- **Vector Database**: ChromaDB
- **Backend API**: FastAPI
- **Frontend**: Streamlit
- **Monitoring**: MLflow
- **Orchestration**: Docker Compose
- **Metadata Storage**: PostgreSQL

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           MEDICAL LITERATURE SOURCES                 │
│  (PDFs, Clinical Guidelines, Research Papers)        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         INGESTION & EMBEDDING PIPELINE               │
│  (Document Parsing → Chunking → BioBERT)            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              CHROMA VECTOR DATABASE                  │
│  (Semantic Search & Retrieval)                      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│            RAG PIPELINE (LangChain)                   │
│  (Query → Retrieval → Context Building)              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              OLLAMA LLM SERVICE                      │
│  (Mistral 7B - Answer Generation)                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│         FASTAPI BACKEND API                          │
│  (REST Endpoints, Response Formatting)               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│           STREAMLIT FRONTEND UI                      │
│  (Medical Professional Interface)                    │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git
- 16GB RAM minimum (32GB optimal)
- 50GB storage

### Setup

1. Clone the repository
```bash
git clone <repository-url>
cd medical-rag-assistant
```

2. Start all services
```bash
docker compose up -d
```

3. Access the application
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs
- ChromaDB: http://localhost:8001

### Development

Install dependencies:
```bash
pip install -r requirements.txt
```

Run tests:
```bash
pytest tests/
```

## Project Structure

```
medical-rag-assistant/
├── src/
│   ├── ingestion/          # Data loading and preprocessing
│   ├── processing/         # RAG pipeline and embeddings
│   ├── models/             # Model training and inference
│   └── api/                # FastAPI endpoints
├── notebooks/              # Exploratory data analysis
├── data/
│   ├── raw/                # Original medical documents
│   ├── processed/          # Cleaned and chunked data
│   └── models/             # Trained models
├── monitoring/             # MLflow and Prometheus configs
├── tests/                  # Unit and integration tests
├── docs/                   # Architecture and API docs
└── docker-compose.yml      # Service orchestration
```

## API Endpoints

- `POST /api/query` - Submit medical question
- `POST /api/ingest` - Ingest new documents
- `GET /api/health` - Health check
- `GET /api/sources` - List indexed sources

## Monitoring

- MLflow UI: http://localhost:5000
- Prometheus metrics: http://localhost:9090

## License

Educational Project - M1 Innovation Week

## Team

- [Team Member 1]
- [Team Member 2]
- [Team Member 3]
