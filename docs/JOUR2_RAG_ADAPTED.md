# Jour 2 - RAG Medical Data Pipeline & Processing

## 🎯 Objectifs du Jour RAG Adaptés

Implémenter une pipeline d'ingestion de documents médicaux
Nettoyer, chunker et valider les textes médicaux
Générer des embeddings avec BioBERT (domaine médical)
Indexer les vecteurs dans ChromaDB + metadata dans PostgreSQL
Analyser les documents et générer insights RAG
Tester la pipeline end-to-end et valider la qualité des embeddings

---

## 🌅 MATINÉE (9h-13h) - Document Ingestion & Processing (4 heures)

### Étape 1 : Concevoir la Pipeline Document Ingestion

Une pipeline RAG médicale c'est : récupérer documents, les chunker, créer des embeddings, indexer. Pas de raccourcis sur la qualité médicale.

**Composants essentiels RAG :**
- **Document Sources** : PDF médicaux, guidelines cliniques, PubMed articles
- **Document Loaders** : LangChain PDF, HTML, DOCX parsers
- **Text Chunking** : Segments intelligents (512 tokens, overlap 50)
- **Medical Cleaning** : Suppression headers/footers, normalisation termes
- **Embedding Generation** : BioBERT/sentence-transformers (domaine médical)
- **Vector Storage** : ChromaDB pour similarité sémantique
- **Metadata Storage** : PostgreSQL pour filtres et recherche
- **Error Handling** : Retry parsing, fallback OCR, logging détaillé
- **Monitoring** : Métriques ingestion (docs/sec, embedding time, storage size)

**Contexte RAG** : Chez les systèmes de recherche médicale comme IBM Watson Health, 40% du temps est passé sur l'ingestion de documents et le chunking. Un mauvais chunking = réponses incohérentes. D'où l'importance de la stratégie de segmentation médicale.

---

### Étape 2 : Implémenter Document Loaders avec LangChain

**LangChain** est le framework standard pour RAG. Choix basé sur le type de document : PDF → PyPDF2/pypdf, HTML → BeautifulSoup.

**Exemple : Document Loader RAG :**

```python
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import logging
from typing import List
from langchain.schema import Document

class MedicalDocumentLoader:
    def __init__(self, data_dir: str = "./data/raw"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialisation loader avec dossier: {data_dir}")

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """Charger un document PDF médical"""
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            self.logger.info(f"PDF chargé: {pdf_path} - {len(documents)} pages")
            return documents
        except Exception as e:
            self.logger.error(f"Erreur chargement PDF {pdf_path}: {e}")
            raise

    def load_text(self, text_path: str) -> List[Document]:
        """Charger un document texte (guidelines, HTML converti)"""
        try:
            loader = TextLoader(text_path)
            documents = loader.load()
            self.logger.info(f"Texte chargé: {text_path}")
            return documents
        except Exception as e:
            self.logger.error(f"Erreur chargement texte {text_path}: {e}")
            raise

    def load_directory(self) -> List[Document]:
        """Charger tous les documents du dossier"""
        all_documents = []
        
        # Charger les PDFs
        pdf_files = list(self.data_dir.glob("*.pdf"))
        for pdf_file in pdf_files:
            try:
                docs = self.load_pdf(str(pdf_file))
                all_documents.extend(docs)
            except Exception as e:
                self.logger.warning(f"Échec chargement {pdf_file}: {e}")
        
        # Charger les fichiers texte
        text_files = list(self.data_dir.glob("*.txt"))
        for text_file in text_files:
            try:
                docs = self.load_text(str(text_file))
                all_documents.extend(docs)
            except Exception as e:
                self.logger.warning(f"Échec chargement {text_file}: {e}")
        
        self.logger.info(f"Total documents chargés: {len(all_documents)}")
        return all_documents
```

---

### Étape 3 : Medical Text Chunking Strategy

Le chunking est critique en RAG. Mauvais chunking = mauvaises réponses.

**Techniques essentielles RAG :**
- **Fixed Size Chunking** : 512 tokens avec overlap 50 (standard)
- **Recursive Chunking** : Respecte paragraphes et phrases
- **Medical Boundary Detection** : Sections médicales (Symptômes, Traitement, etc.)
- **Metadata Preservation** : Conserver titre, auteurs, journal
- **Overlap Strategy** : 50 tokens pour cohérence contextuelle

**Exemple : Medical Chunker :**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document

class MedicalTextChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Splitter récursif respectant les boundaries naturelles
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.logger = logging.getLogger(__name__)

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Diviser les documents en chunks médicaux"""
        chunks = []
        
        for doc in documents:
            # Chunking avec préservation metadata
            doc_chunks = self.splitter.split_documents([doc])
            
            # Ajouter metadata de chunk
            for i, chunk in enumerate(doc_chunks):
                chunk.metadata.update({
                    "chunk_id": f"{doc.metadata.get('source', 'unknown')}_{i}",
                    "chunk_index": i,
                    "total_chunks": len(doc_chunks),
                    "original_length": len(doc.page_content)
                })
                chunks.append(chunk)
        
        self.logger.info(f"Chunking complété: {len(documents)} docs → {len(chunks)} chunks")
        return chunks

    def analyze_chunks(self, chunks: List[Document]):
        """Analyser la distribution des tailles de chunks"""
        lengths = [len(chunk.page_content) for chunk in chunks]
        
        stats = {
            "total_chunks": len(chunks),
            "avg_length": sum(lengths) / len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "median_length": sorted(lengths)[len(lengths) // 2]
        }
        
        self.logger.info(f"Statistiques chunks: {stats}")
        return stats
```

---

### Étape 4 : Medical Text Cleaning & Preprocessing

Nettoyage spécifique domaine médical pour maximiser la qualité des embeddings.

**Techniques médicales :**
- **Suppression Headers/Footers** : Numéros de pages, copyright
- **Normalisation Terminologique** : Termes médicaux, abréviations
- **Références Bibliographiques** : Suppression si non pertinentes
- **Unicode Normalization** : Accents, caractères spéciaux
- **Stop Words Médicaux** : Terms trop fréquents en médical

**Exemple : Medical Text Cleaner :**

```python
import re
from typing import List
from langchain.schema import Document

class MedicalTextCleaner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns à supprimer
        self.patterns_to_remove = [
            r'© \d{4}.*',  # Copyright
            r'Page \d+ of \d+',  # Numéros de pages
            r'\[\d+\]',  # Références numériques
            r'http[s]?://\S+',  # URLs
            r'\b\d{1,2}:\d{2}\b',  # Horaires
        ]

    def clean_text(self, text: str) -> str:
        """Nettoyer un texte médical"""
        cleaned = text
        
        # Supprimer patterns
        for pattern in self.patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Normaliser espaces
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Supprimer lignes vides multiples
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        
        return cleaned

    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """Nettoyer tous les documents"""
        cleaned_docs = []
        
        for doc in documents:
            cleaned_content = self.clean_text(doc.page_content)
            if cleaned_content:  # Garder seulement si non vide
                cleaned_docs.append(
                    Document(
                        page_content=cleaned_content,
                        metadata=doc.metadata
                    )
                )
        
        self.logger.info(f"Nettoyage: {len(documents)} → {len(cleaned_docs)} docs")
        return cleaned_docs
```

---

### Étape 5 : Embedding Generation avec BioBERT

Les embeddings déterminent 90% de la qualité RAG. BioBERT est pré-entraîné sur corpus biomédical.

**Techniques embeddings médicaux :**
- **BioBERT** : Pre-trained sur PubMed + MIMIC-III
- **Sentence-Transformers** : all-MiniLM-L6-v2 (plus léger)
- **Batch Processing** : Traitement par lots pour performance
- **Normalization** : L2 normalization des vecteurs
- **Caching** : Sauvegarder embeddings calculés

**Exemple : Medical Embedding Generator :**

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from langchain.schema import Document

class MedicalEmbeddingGenerator:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Chargement modèle: {model_name}")
        
        # Charger le modèle
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Générer embeddings pour une liste de textes"""
        self.logger.info(f"Génération embeddings pour {len(texts)} textes")
        
        # Générer embeddings
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Normalizer L2
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        self.logger.info(f"Embeddings générés: shape {embeddings.shape}")
        return embeddings

    def generate_document_embeddings(self, documents: List[Document]) -> List[np.ndarray]:
        """Générer embeddings pour les documents/chunks"""
        texts = [doc.page_content for doc in documents]
        embeddings = self.generate_embeddings(texts)
        return embeddings
```

---

### Étape 6 : Vector Indexation avec ChromaDB

Stocker les embeddings pour recherche sémantique rapide.

**Composants ChromaDB :**
- **Collection Creation** : Par type de document (articles, guidelines)
- **Metadata Indexing** : Filtrage par date, spécialité
- **Batch Insertion** : Insertion par lots pour performance
- **Persistence** : Volumes Docker pour persistence

**Exemple : ChromaDB Indexer :**

```python
import chromadb
from chromadb.config import Settings
from typing import List
from langchain.schema import Document

class ChromaIndexer:
    def __init__(self, collection_name: str = "medical_documents"):
        self.logger = logging.getLogger(__name__)
        
        # Client ChromaDB
        self.client = chromadb.PersistentClient(path="./data/chroma_db")
        
        # Créer ou récupérer collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Medical RAG documents"}
        )
        
        self.logger.info(f"Collection ChromaDB: {collection_name}")

    def index_documents(self, documents: List[Document], embeddings: List[np.ndarray]):
        """Indexer documents avec embeddings"""
        self.logger.info(f"Indexation de {len(documents)} documents")
        
        # Préparer les données
        ids = [f"doc_{i}" for i in range(len(documents))]
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Ajouter à ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas
        )
        
        self.logger.info(f"Indexation terminée: {len(documents)} docs indexés")

    def query_similar(self, query_embedding: np.ndarray, n_results: int = 5):
        """Recherche de documents similaires"""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results
        )
        return results
```

---

## ☀️ APRÈS-MIDI (14h-17h) - EDA RAG & Validation (3 heures)

### Étape 7 : Exploratory Data Analysis RAG

Comprendre vos documents et embeddings avant le RAG : distributions de chunks, qualité des embeddings, couverture thématique.

**Script EDA RAG :**

```python
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

class RAGDataExplorer:
    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.logger = logging.getLogger(__name__)

    def basic_document_stats(self):
        """Statistiques de base des documents"""
        print(f"=== Document Statistics ===")
        print(f"Total documents: {len(self.documents)}")
        
        # Distribution des longueurs
        lengths = [len(doc.page_content) for doc in self.documents]
        print(f"Average length: {sum(lengths) / len(lengths):.2f}")
        print(f"Min length: {min(lengths)}")
        print(f"Max length: {max(lengths)}")
        
        return lengths

    def metadata_analysis(self):
        """Analyser les métadonnées"""
        print(f"\n=== Metadata Analysis ===")
        
        # Sources
        sources = [doc.metadata.get('source', 'unknown') for doc in self.documents]
        source_counts = Counter(sources)
        print(f"Sources: {source_counts}")
        
        # Types de documents
        doc_types = [doc.metadata.get('type', 'unknown') for doc in self.documents]
        type_counts = Counter(doc_types)
        print(f"Document types: {type_counts}")

    def plot_length_distribution(self, lengths: List[int]):
        """Visualiser distribution des longueurs"""
        plt.figure(figsize=(10, 6))
        plt.hist(lengths, bins=50, edgecolor='black')
        plt.xlabel('Document Length (characters)')
        plt.ylabel('Frequency')
        plt.title('Distribution of Document Lengths')
        plt.savefig('./data/eda/length_distribution.png')
        plt.close()
```

---

### Étape 8 : Pipeline de Stockage et Versioning RAG

Après transformation, stocker les embeddings et documents de manière versionnée.

**Exemple : RAG Data Store :**

```python
import json
from pathlib import Path
from datetime import datetime

class RAGDataStore:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
    def save_indexed_documents(self, documents: List[Document], version: str = "v1"):
        """Sauvegarder documents indexés"""
        # Sauvegarder en JSON (pour simplicity RAG)
        data = [{
            'content': doc.page_content,
            'metadata': doc.metadata
        } for doc in documents]
        
        path = self.processed_dir / f"medical_docs_{version}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Metadata
        metadata = {
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'total_documents': len(documents),
            'avg_length': sum(len(d.page_content) for d in documents) / len(documents)
        }
        
        meta_path = self.processed_dir / f"medical_docs_{version}_meta.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return str(path), metadata
```

---

### Étape 9 : Tests de Qualité RAG

Garantir que les données RAG sont prêtes avant J3.

**Tests qualité RAG :**

```python
class RAGQualityTests:
    def __init__(self, documents: List[Document]):
        self.documents = documents
        self.passed = 0
        self.failed = 0

    def test_no_empty_documents(self):
        """Vérifier absence de documents vides"""
        empty = [d for d in self.documents if not d.page_content.strip()]
        if empty:
            print(f"FAIL: {len(empty)} documents vides")
            self.failed += 1
        else:
            print("PASS: No empty documents")
            self.passed += 1

    def test_chunk_size_range(self, min_size: int = 50, max_size: int = 2000):
        """Vérifier que les chunks ont une taille raisonnable"""
        out_of_range = [
            d for d in self.documents 
            if len(d.page_content) < min_size or len(d.page_content) > max_size
        ]
        if out_of_range:
            print(f"FAIL: {len(out_of_range)} chunks hors range [{min_size}, {max_size}]")
            self.failed += 1
        else:
            print(f"PASS: All chunks in range [{min_size}, {max_size}]")
            self.passed += 1

    def test_metadata_completeness(self, required_fields: List[str]):
        """Vérifier que les métadonnées requises sont présentes"""
        missing = []
        for doc in self.documents:
            for field in required_fields:
                if field not in doc.metadata:
                    missing.append((doc.metadata.get('chunk_id', 'unknown'), field))
        
        if missing:
            print(f"FAIL: {len(missing)} metadata manquantes")
            self.failed += 1
        else:
            print("PASS: All required metadata present")
            self.passed += 1

    def report(self):
        """Résumé tests"""
        total = self.passed + self.failed
        print(f"\n=== RAG Quality Report ===")
        print(f"Passed: {self.passed}/{total}")
        print(f"Failed: {self.failed}/{total}")
        return self.failed == 0
```

---

## 📋 Résumé Jour 2 RAG Adapté

✓ **Pipeline Document Ingestion** implémentée et testée
✓ **Medical Chunking** avec préservation boundaries
✓ **Embeddings BioBERT** générés (domaine médical)
✓ **ChromaDB Indexation** avec metadata
✓ **EDA RAG** réalisée avec insights documents
✓ **Qualité RAG validée** (chunks cohérents, embeddings OK)
✓ **Dataset RAG-ready** sauvegardé et versionné

---

## 🚀 Livrables Attendus RAG

- `src/ingestion/medical_loader.py` avec Document Loaders
- `src/processing/chunker.py` avec Medical Chunking Strategy
- `src/processing/embeddings.py` avec BioBERT Generator
- `src/processing/chroma_indexer.py` avec Vector Indexation
- `tests/test_rag_pipeline.py` avec 5+ tests qualité RAG
- `data/processed/medical_docs_v1.json` + metadata
- `notebooks/01_rag_eda.ipynb` avec visualisations documents
- `README_RAG_J2.md` expliquant transformations RAG
