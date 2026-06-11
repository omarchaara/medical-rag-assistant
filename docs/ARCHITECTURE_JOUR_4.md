
=================================Architecture jour 4============================================

                           ┌──────────────────────┐
                           │   Utilisateur        │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │     Streamlit UI     │
                           │ Dashboard Médical    │
                           └──────────┬───────────┘
                                      │ API Calls
                                      ▼
                           ┌──────────────────────┐
                           │    FastAPI Backend   │
                           │ Endpoints REST       │
                           └──────────┬───────────┘
                                      │
             ┌────────────────────────┼────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
 ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
 │   ChromaDB       │    │     Ollama       │    │    PostgreSQL    │
 │ Vector Search    │    │ Mistral 7B LLM   │    │ Métadonnées      │
 └──────────────────┘    └──────────────────┘    └──────────────────┘
             │
             ▼
 ┌──────────────────┐
 │     MLflow       │
 │ Tracking & Logs  │
 └──────────────────┘

        Tous les services sont orchestrés par Docker Compose

    