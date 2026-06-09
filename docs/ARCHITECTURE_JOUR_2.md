
==================================== Architecture Jour 2 ==========================================

PDF médical
      ↓
Extraction texte
      ↓
Nettoyage
      ↓
Validation qualité
      ↓
Chunking
      ↓
Métadonnées
      ↓
PostgreSQL
      ↓
Parquet

=============================================================================================================

data/raw/
    |
    +-- hypertension_guideline.pdf
    +-- diabetes_guideline.pdf

            ↓

Data Loader

            ↓

Text Extractor

            ↓

Data Validator

            ↓

Data Cleaner

            ↓

Chunk Generator

            ↓

Feature Engineering

            ↓

PostgreSQL + Parquet


==============================================Structure du projet==============================================

medical-rag-assistant/

src/

├── ingestion/
│   ├── loader.py
│   ├── extractor.py
│   ├── validator.py
│   ├── cleaner.py
│   └── pipeline.py
│
├── processing/
│   ├── chunker.py
│   ├── metadata.py
│   └── datastore.py
│
├── tests/
│   └── quality.py
│
data/
│
├── raw/
│
├── processed/
│
└── parquet/

