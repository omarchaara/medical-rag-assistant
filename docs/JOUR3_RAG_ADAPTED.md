# Jour 3 - RAG Model Training & Optimization

## 🎯 Objectifs RAG Spécifiques

Concevoir et entraîner des modèles d'embeddings pour RAG médical
Comparer les stratégies de retrieval avec MLflow tracking
Sélectionner le meilleur embedding model avec justification
Mettre en place la reproductibilité et le versioning des modèles RAG
Documenter l'expérimentation RAG pour audit et traçabilité
Préparer le système RAG pour la production J4

---

## 🌅 MATINÉE (9h-13h) - Baseline RAG & Embedding Models (4 heures)

### Étape 1 : Baseline RAG - Le Point de Référence

Avant d'optimiser, établir une baseline RAG simple. C'est votre "control" : tout système RAG doit dépasser la baseline.

**Approches baseline RAG :**
- **TF-IDF + Cosine Similarity** : Approche classique sans embeddings
- **Random Retrieval** : Sélection aléatoire de chunks (lower bound)
- **No Chunking** : Documents entiers (pour comparer l'impact du chunking)

**Exemple : Baseline RAG TF-IDF :**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGBaseline:
    def __init__(self, retrieval_type='tfidf'):
        self.retrieval_type = retrieval_type
        self.vectorizer = None
        self.chunks = None
        
    def fit(self, chunks):
        """Indexer les chunks avec baseline"""
        self.chunks = chunks
        if self.retrieval_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(max_features=1000)
            self.vectorizer.fit([chunk.page_content for chunk in chunks])
            self.chunk_vectors = self.vectorizer.transform([chunk.page_content for chunk in chunks])
        elif self.retrieval_type == 'random':
            # No vectorization needed for random
            pass
            
    def retrieve(self, query, k=5):
        """Récupérer k chunks pour une query"""
        if self.retrieval_type == 'tfidf':
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.chunk_vectors).flatten()
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            return [self.chunks[i] for i in top_k_indices], similarities[top_k_indices]
        elif self.retrieval_type == 'random':
            indices = np.random.choice(len(self.chunks), min(k, len(self.chunks)), replace=False)
            return [self.chunks[i] for i in indices], np.random.rand(len(indices))
    
    def evaluate(self, test_queries, ground_truth):
        """Évaluer retrieval quality"""
        # Simplifié : mean reciprocal rank (MRR)
        scores = []
        for query, relevant_ids in test_queries:
            retrieved_chunks, _ = self.retrieve(query, k=5)
            retrieved_ids = [chunk.metadata['chunk_id'] for chunk in retrieved_chunks]
            
            # MRR
            for i, ret_id in enumerate(retrieved_ids):
                if ret_id in relevant_ids:
                    scores.append(1 / (i + 1))
                    break
            else:
                scores.append(0)
        
        return {
            'mean_reciprocal_rank': np.mean(scores),
            'baseline_type': self.retrieval_type
        }
```

---

### Étape 2 : MLflow pour RAG Tracking

MLflow pour tracker les expériences RAG : embedding models, chunk strategies, retrieval performance.

**MLflow RAG Tracking :**

```python
import mlflow
from mlflow.sklearn import log_model
import json
from sentence_transformers import SentenceTransformer

class RAGMLflowTracker:
    def __init__(self, experiment_name="rag_medical_experiments"):
        mlflow.set_experiment(experiment_name)
        
    def log_embedding_experiment(self, model_name, embedding_model, 
                                chunks, test_queries, chunk_strategy):
        """Logger une expérience d'embedding RAG"""
        with mlflow.start_run(run_name=model_name):
            # Log hyperparams
            mlflow.log_params({
                'model_name': model_name,
                'chunk_size': chunk_strategy['chunk_size'],
                'chunk_overlap': chunk_strategy['chunk_overlap'],
                'embedding_dim': embedding_model.get_sentence_embedding_dimension()
            })
            
            # Generate embeddings
            chunk_texts = [chunk.page_content for chunk in chunks]
            chunk_embeddings = embedding_model.encode(chunk_texts)
            
            # Log embedding stats
            mlflow.log_metric("num_chunks", len(chunks))
            mlflow.log_metric("avg_embedding_norm", np.mean(np.linalg.norm(chunk_embeddings, axis=1)))
            
            # Test retrieval
            mrr_scores = []
            retrieval_times = []
            
            for query, relevant_ids in test_queries:
                query_embedding = embedding_model.encode([query])
                
                # Retrieval timing
                import time
                start = time.time()
                similarities = cosine_similarity(query_embedding, chunk_embeddings).flatten()
                top_k_indices = np.argsort(similarities)[-5:][::-1]
                end = time.time()
                
                retrieval_times.append(end - start)
                
                # MRR calculation
                for i, idx in enumerate(top_k_indices):
                    if chunks[idx].metadata['chunk_id'] in relevant_ids:
                        mrr_scores.append(1 / (i + 1))
                        break
                else:
                    mrr_scores.append(0)
            
            # Log metrics
            mlflow.log_metric("mean_reciprocal_rank", np.mean(mrr_scores))
            mlflow.log_metric("avg_retrieval_time_ms", np.mean(retrieval_times) * 1000)
            
            # Log chunking stats
            chunk_lengths = [len(chunk.page_content) for chunk in chunks]
            mlflow.log_metric("avg_chunk_length", np.mean(chunk_lengths))
            
            # Log metadata
            metadata = {
                'model_name': model_name,
                'num_chunks': len(chunks),
                'chunk_strategy': chunk_strategy,
                'test_queries': len(test_queries)
            }
            
            with open("experiment_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            mlflow.log_artifact("experiment_metadata.json")
            
            return {
                'mrr': np.mean(mrr_scores),
                'avg_time_ms': np.mean(retrieval_times) * 1000,
                'run_id': mlflow.active_run().info.run_id
            }
```

---

### Étape 3 : Entraîner Modèles d'Embeddings Avancés

Selon votre domaine médical : généralistes vs spécialisés biomedical.

**Modèles embeddings recommandés :**
- **Généralistes** : all-MiniLM-L6-v2, all-mpnet-base-v2
- **Spécialisés médical** : BioBERT, PubMedBERT, ClinicalBERT
- **Multilingues** : paraphrase-multilingual-MiniLM-L12-v2

**Comparaison d'Embedding Models :**

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModelComparator:
    def __init__(self):
        self.models = {}
        
    def add_model(self, model_name, model_path):
        """Ajouter un modèle à comparer"""
        self.models[model_name] = {
            'model': SentenceTransformer(model_path),
            'embedding_dim': None,
            'download_size': None
        }
        # Get info
        model = SentenceTransformer(model_path)
        self.models[model_name]['embedding_dim'] = model.get_sentence_embedding_dimension()
        
    def compare_models(self, chunks, test_queries):
        """Comparer plusieurs embedding models"""
        results = []
        
        for model_name, model_info in self.models.items():
            model = model_info['model']
            
            # Generate embeddings
            chunk_texts = [chunk.page_content for chunk in chunks]
            chunk_embeddings = model.encode(chunk_texts, show_progress_bar=False)
            
            # Test retrieval
            mrr_scores = []
            
            for query, relevant_ids in test_queries:
                query_embedding = model.encode([query])
                similarities = cosine_similarity(query_embedding, chunk_embeddings).flatten()
                top_k_indices = np.argsort(similarities)[-5:][::-1]
                
                for i, idx in enumerate(top_k_indices):
                    if chunks[idx].metadata['chunk_id'] in relevant_ids:
                        mrr_scores.append(1 / (i + 1))
                        break
                else:
                    mrr_scores.append(0)
            
            results.append({
                'Model': model_name,
                'Embedding Dim': model_info['embedding_dim'],
                'MRR': np.mean(mrr_scores),
                'Model_Object': model
            })
        
        return results
```

---

## ☀️ APRÈS-MIDI (14h-17h) - Chunking Strategy Tuning (3 heures)

### Étape 4 : Chunking Strategy Experiments

Le chunking impacte massivement la qualité RAG. Tester différentes stratégies.

**Stratégies de chunking à tester :**
- **Fixed Size** : 256, 512, 1024 caractères
- **Semantic** : Par phrases, par paragraphes
- **Sliding Window** : Différents overlaps (25, 50, 100 tokens)
- **Medical-aware** : Respect des sections médicales

**Chunking Experiments :**

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ChunkingStrategyTester:
    def __init__(self, documents):
        self.documents = documents
        
    def test_chunking_strategy(self, strategy_config, embedding_model, test_queries):
        """Tester une stratégie de chunking"""
        # Create chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=strategy_config['chunk_size'],
            chunk_overlap=strategy_config.get('chunk_overlap', 50),
            length_function=len,
            separators=strategy_config.get('separators', ["\n\n", "\n", ". ", " ", ""])
        )
        
        chunks = splitter.split_documents(self.documents)
        
        # Add metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                'chunk_id': f"{strategy_config['name']}_{i}",
                'strategy': strategy_config['name']
            })
        
        # Test retrieval
        chunk_embeddings = embedding_model.encode([c.page_content for c in chunks])
        mrr_scores = []
        
        for query, relevant_ids in test_queries:
            query_embedding = embedding_model.encode([query])
            similarities = cosine_similarity(query_embedding, chunk_embeddings).flatten()
            top_k_indices = np.argsort(similarities)[-5:][::-1]
            
            for i, idx in enumerate(top_k_indices):
                if chunks[idx].metadata.get('chunk_id') in relevant_ids:
                    mrr_scores.append(1 / (i + 1))
                    break
            else:
                mrr_scores.append(0)
        
        return {
            'strategy': strategy_config['name'],
            'chunk_size': strategy_config['chunk_size'],
            'num_chunks': len(chunks),
            'avg_chunk_length': np.mean([len(c.page_content) for c in chunks]),
            'mrr': np.mean(mrr_scores),
            'chunks': chunks
        }
```

---

### Étape 5 : RAG Quality Validation

Tests qualité pour systèmes RAG : coherence, relevancy, latency.

**RAG Quality Tests :**

```python
class RAGSystemValidator:
    def __init__(self, retrieval_system, test_queries):
        self.retrieval_system = retrieval_system
        self.test_queries = test_queries
        
    def test_retrieval_relevance(self):
        """Tester la pertinence des résultats"""
        relevance_scores = []
        
        for query, relevant_ids in self.test_queries:
            retrieved_chunks, scores = self.retrieval_system.retrieve(query, k=5)
            retrieved_ids = [c.metadata['chunk_id'] for c in retrieved_chunks]
            
            # Relevance@5
            relevant_retrieved = len(set(retrieved_ids) & set(relevant_ids))
            relevance_scores.append(relevant_retrieved / 5)
        
        print(f"Average Relevance@5: {np.mean(relevance_scores):.3f}")
        assert np.mean(relevance_scores) > 0.5, "Relevance too low"
        print("✓ Retrieval relevance acceptable")
        
    def test_response_time(self, max_time_ms=100):
        """Tester temps de réponse"""
        import time
        
        query = test_queries[0][0]
        
        times = []
        for _ in range(10):
            start = time.time()
            self.retrieval_system.retrieve(query, k=5)
            end = time.time()
            times.append((end - start) * 1000)
        
        avg_time = np.mean(times)
        print(f"Average retrieval time: {avg_time:.2f}ms")
        assert avg_time < max_time_ms, f"Response time too high: {avg_time:.2f}ms"
        print("✓ Response time acceptable")
        
    def test_answer_coherence(self, llm_client):
        """Tester la cohérence des réponses générées"""
        # Pour J5 quand LLM sera intégré
        print("⚠️ LLM coherence test deferred to J5")
```

---

### Étape 6 : Enregistrer Système RAG dans MLflow Registry

Versionner le système RAG complet pour J4 (API).

**RAG System Registry :**

```python
def register_rag_system(best_config, best_model, best_chunks, registry_name="medical_rag_system"):
    """Enregistrer le système RAG complet dans MLflow Registry"""
    
    with mlflow.start_run(run_name="final_rag_system"):
        # Log configuration
        mlflow.log_params({
            'embedding_model': best_config['model_name'],
            'chunk_size': best_config['chunk_size'],
            'chunk_overlap': best_config['chunk_overlap'],
            'retrieval_k': 5
        })
        
        # Log metrics
        mlflow.log_metrics(best_config['metrics'])
        
        # Save chunks
        import json
        chunks_data = [{
            'content': chunk.page_content,
            'metadata': chunk.metadata
        } for chunk in best_chunks]
        
        with open("chunks.json", 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=2, ensure_ascii=False)
        mlflow.log_artifact("chunks.json")
        
        # Register system
        # Note: Pour RAG, on enregistre la config plutôt que le modèle sklearn
        model_info = mlflow.pyfunc.log_model(
            python_model="retrieval_wrapper.py",
            artifacts={"chunks": "chunks.json"}
        )
        
        mv = mlflow.register_model(model_info.model_uri, registry_name)
        
        # Transition to Production
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=registry_name,
            version=mv.version,
            stage="Production"
        )
        
        print(f"RAG System registered as {registry_name} v{mv.version} (Production)")
        return mv.version
```

---

## 📋 Résumé Jour 3 RAG Adapté

✓ Baseline RAG établie (TF-IDF + Random)
✓ 3+ embedding models comparés (généralistes vs médicaux)
✓ MLflow tracking complet (embeddings + chunking)
✓ Chunking strategy tuning (size, overlap, semantic)
✓ Meilleur système RAG sélectionné avec justification
✓ Tests RAG validation (relevance, latency)
✓ Système RAG enregistré en MLflow Registry (Production)

---

## 🚀 Livrables Attendus RAG

- `src/models/embedding_comparator.py` - Comparaison embedding models
- `src/models/chunking_tester.py` - Tests stratégies chunking
- `src/models/rag_validator.py` - Validation système RAG
- `src/models/train.py` - Pipeline d'entraînement RAG complet
- Embedding model enregistré dans MLflow Registry
- Tableau comparatif des stratégies (CSV/JSON)
- Justification du système RAG choisi
- Tests validation passants
