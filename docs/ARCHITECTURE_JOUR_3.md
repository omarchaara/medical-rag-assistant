
================Architecture jour 3=======================================================

                        ┌──────────────────────┐
                        │  PDF Médicaux        │
                        │  (data/raw)          │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  ETL Pipeline        │
                        │  Extraction          │
                        │  Nettoyage           │
                        │  Chunking            │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │  Embeddings          │
                        │ SentenceTransformers │
                        │ BioBERT              │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ ChromaDB             │
                        │ Vector Database      │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Similarity Search    │
                        │ Top-K Retrieval      │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ Context Retrieval    │
                        │ pour LLM             │
                        └──────────────────────┘

