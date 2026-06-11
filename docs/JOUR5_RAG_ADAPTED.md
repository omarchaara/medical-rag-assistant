# JOUR 5 - PRODUCTION & PRÉSENTATION - ADAPTATION RAG

## 🎯 OBJECTIFS DU JOUR 5 - VERSION RAG MÉDICAL

Adapter le Jour 5 (Production & Présentation) du guide ML classique au contexte spécifique du projet **Medical RAG Assistant**.

---

## 📋 ADAPTATIONS PRINCIPALES

### **ML Classique → RAG Médical**

| Aspect ML Classique | Aspect RAG Médical | Justification |
|-------------------|-------------------|---------------|
| **Prédictions/sec** | **Requêtes RAG/sec** | RAG fait retrieval, pas classification |
| **Accuracy metric** | **MRR (Mean Reciprocal Rank)** | Métrique retrieval pertinente |
| **Model latency** | **Retrieval latency** | Temps pour récupérer chunks pertinents |
| **Batch predictions** | **Batch retrieval** | Traiter plusieurs requêtes médicales en parallèle |
| **Model performance** | **System performance** | Pipeline complet (ingestion → retrieval → réponse) |

---

## 🌅 MATINÉE (9h-13h) - MONITORING & QUALITY ASSURANCE RAG

### **Étape 1 : Monitoring avec Prometheus & Grafana - Adaptation RAG**

#### **Configuration Prometheus (prometheus.yml)**

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'rag_api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'

  - job_name: 'mlflow'
    static_configs:
      - targets: ['mlflow:5000']
    metrics_path: '/metrics'

  - job_name: 'chromadb'
    static_configs:
      - targets: ['chromadb:8001']
      
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
```

#### **Métriques RAG Spécifiques**

**Métriques à tracker :**
- `rag_requests_total` - Total des requêtes RAG
- `rag_retrieval_time_seconds` - Temps de retrieval
- `rag_chunks_retrieved` - Nombre de chunks récupérés
- `rag_mrr_score` - Mean Reciprocal Rank
- `rag_embedding_time_seconds` - Temps d'embeddings
- `rag_errors_total` - Erreurs RAG (par type)

---

### **Étape 2 : Instrumenter l'API RAG avec Prometheus**

#### **Code instrumentation RAG**

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Métriques RAG spécifiques
rag_requests_total = Counter(
    'rag_requests_total',
    'Total RAG requests',
    ['endpoint', 'status']
)

rag_retrieval_time = Histogram(
    'rag_retrieval_time_seconds',
    'RAG retrieval latency',
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0)
)

rag_chunks_retrieved = Histogram(
    'rag_chunks_retrieved',
    'Number of chunks retrieved per query',
    buckets=(1, 2, 3, 5, 10)
)

rag_mrr_score = Gauge(
    'rag_mrr_score',
    'Current MRR score for retrieval quality'
)

rag_errors_total = Counter(
    'rag_errors_total',
    'Total RAG errors',
    ['error_type']
)

@app.post("/query")
async def rag_query(query: RAGQuery):
    with rag_retrieval_time.time():
        try:
            # 1. Embedding de la query
            start_embed = time.time()
            query_embedding = model.encode([query.text])
            embed_time = time.time() - start_embed
            
            # 2. Retrieval des chunks
            start_retrieval = time.time()
            chunks = vector_store.search(query_embedding, k=5)
            retrieval_time = time.time() - start_retrieval
            
            # 3. Génération de réponse (simulation)
            response = generate_response(chunks, query.text)
            
            # Métriques
            rag_requests_total.labels(endpoint='/query', status='success').inc()
            rag_chunks_retrieved.observe(len(chunks))
            
            return {
                "response": response,
                "chunks": chunks,
                "metrics": {
                    "embed_time": embed_time,
                    "retrieval_time": retrieval_time,
                    "chunks_count": len(chunks)
                }
            }
            
        except VectorStoreError as e:
            rag_errors_total.labels(error_type='vector_store').inc()
            raise HTTPException(status_code=500, detail="Vector store error")
        except EmbeddingError as e:
            rag_errors_total.labels(error_type='embedding').inc()
            raise HTTPException(status_code=500, detail="Embedding error")
        except Exception as e:
            rag_errors_total.labels(error_type='unknown').inc()
            raise

@app.get("/metrics")
async def metrics():
    """Endpoint Prometheus"""
    return generate_latest()
```

---

### **Étape 3 : Tests End-to-End RAG**

#### **Test Suite E2E RAG**

```python
import pytest
from fastapi.testclient import TestClient
import time
import json

client = TestClient(app)

class TestRAGE2E:
    @pytest.fixture(scope="class")
    def setup(self):
        """Setup avant tous les tests RAG"""
        # Vérifier health
        response = client.get("/health")
        assert response.status_code == 200
        
        # Vérifier vector store
        response = client.get("/vector_store/status")
        assert response.status_code == 200
        
        yield
        # Cleanup après

    def test_full_rag_pipeline(self):
        """Test complet RAG : query → embedding → retrieval → response"""
        # 1. Query médicale
        test_query = {
            "text": "symptoms of diabetes type 2"
        }

        # 2. Exécuter requête RAG
        response = client.post("/query", json=test_query)
        assert response.status_code == 200
        result = response.json()

        # 3. Vérifier réponse valide
        assert "response" in result
        assert "chunks" in result
        assert "metrics" in result
        assert len(result["chunks"]) > 0
        assert result["metrics"]["retrieval_time"] < 1.0

    def test_retrieval_performance(self):
        """Tester latence retrieval < 500ms"""
        test_query = {"text": "diabetes treatment"}
        
        start = time.time()
        response = client.post("/query", json=test_query)
        duration = time.time() - start

        assert response.status_code == 200
        result = response.json()
        assert duration < 0.5, f"Total latency {duration*1000:.2f}ms > 500ms"
        assert result["metrics"]["retrieval_time"] < 0.3

    def test_batch_rag_queries(self):
        """Batch requêtes RAG : 50 queries < 10sec"""
        medical_queries = [
            {"text": "diabetes symptoms"},
            {"text": "heart disease prevention"},
            {"text": "asthma treatment"},
            {"text": "hypertension management"},
            {"text": "kidney disease symptoms"}
        ] * 10  # 50 queries total

        start = time.time()
        responses = []
        for query in medical_queries:
            response = client.post("/query", json=query)
            responses.append(response)
        duration = time.time() - start

        # Vérifier toutes les requêtes réussies
        assert all(r.status_code == 200 for r in responses)
        assert duration < 10, f"Batch took {duration:.2f}s > 10s"

    def test_embedding_quality(self):
        """Tester qualité des embeddings"""
        similar_queries = [
            {"text": "diabetes symptoms"},
            {"text": "signs of diabetes"}
        ]
        
        responses = []
        for query in similar_queries:
            response = client.post("/query", json=query)
            responses.append(response.json())
        
        # Vérifier que les queries similaires récupèrent des chunks similaires
        chunks1 = [c["id"] for c in responses[0]["chunks"]]
        chunks2 = [c["id"] for c in responses[1]["chunks"]]
        
        # Au moins un chunk commun
        overlap = set(chunks1) & set(chunks2)
        assert len(overlap) > 0, "Similar queries should retrieve similar chunks"

    def test_monitoring_endpoint(self):
        """Vérifier metrics RAG collectées"""
        response = client.get("/metrics")
        assert response.status_code == 200
        content = response.content.decode()
        
        # Vérifier métriques RAG
        assert 'rag_requests_total' in content
        assert 'rag_retrieval_time_seconds' in content
        assert 'rag_chunks_retrieved' in content
        assert 'rag_mrr_score' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## ☀️ APRÈS-MIDI (14h-17h) - PRÉSENTATION & DÉMO RAG

### **Étape 4 : Structure Présentation RAG (15 min)**

#### **Slides Adaptées RAG**

**Slide 1 (1 min) : Title + Team**
- "Medical RAG Assistant : IA d'assistance médicale basée sur RAG"
- Équipe et contexte du projet

**Slide 2 (2 min) : Le Problème**
- Accès limité à l'information médicale
- Recherche manuelle chronophage
- Besoin d'assistant IA contextuel pour professionnels de santé
- Challenge : Fiabilité des réponses médicales

**Slide 3 (1 min) : La Solution RAG**
- Retrieval-Augmented Generation pour domaines médicaux
- Pipeline : Documents → Chunking → Embeddings → Retrieval → Réponses
- Avantages : Réponses contextuelles, sourcées, explicables
- Technologies : LangChain + ChromaDB + Sentence-Transformers

**Slide 4 (3 min) : Démo Live RAG**
- Démonstration du pipeline RAG en action
- Query médicale → Retrieval de chunks pertinents → Réponse générée
- Visualisation des embeddings et similarité

**Slide 5 (1 min) : Architecture Technique**
- Ingestion des documents médicaux (PDF, DOCX, TXT)
- Chunking intelligent avec overlap
- Embedding models (MiniLM-L6-v2, BioBERT-ready)
- Vector database (ChromaDB) + MLflow tracking

**Slide 6 (1 min) : Résultats**
- MRR (Mean Reciprocal Rank) : 1.000 (testing)
- Retrieval latency : <50ms
- 5+ modèles d'embeddings comparés
- Baselines RAG validées

**Slide 7 (1 min) : Apprentissages + Futur**
- Défis : Qualité des données médicales, Scalability
- Améliorations : BioBERT spécialisé, Multi-modal (images + texte)
- Déploiement production : API + Monitoring + Tests E2E

**Slide 8 (0.5 min) : Thank You**
- Repository GitHub
- Q&A

---

### **Étape 5 : Démonstration Live RAG**

#### **Script Démo RAG**

```python
# DEMO_SCRIPT_RAG.md

## SCÉNARIO DÉMO LIVE (3 minutes)

### 0:00 - Introduction (30s)
"Bonjour, je vais vous présenter notre Medical RAG Assistant.
C'est un assistant IA basé sur RAG pour aider les professionnels de santé 
à accéder rapidement à l'information médicale pertinente."

### 0:30 - Setup (30s)
[Dans terminal 1]
"Je lance d'abord notre API FastAPI"
uvicorn src.api.main:app --reload

[Dans terminal 2]  
"Et l'interface Streamlit"
streamlit run src/frontend/app.py

"Dans un autre terminal, MLflow pour le tracking"
mlflow ui

### 1:00 - Présentation Streamlit (1 min)
"Voici notre interface utilisateur.
Ici les professionnels de santé peuvent poser des questions médicales."

[Sur Streamlit - demo_query]
"Par exemple : 'Quels sont les symptômes du diabète de type 2 ?'"

[Click sur 'Query']
"L'application fait le retrieval des chunks pertinents dans notre base 
de documents médicaux."

"Vous voyez ici les 5 chunks les plus pertinents avec leurs scores de similarité."

### 2:00 - Pipeline RAG (30s)
"Behind the scenes, le pipeline RAG fait :
1. Embedding de la query avec MiniLM-L6-v2
2. Retrieval vectoriel dans ChromaDB  
3. Génération de réponse contextuelle
4. Affichage des sources pour vérification"

### 2:30 - MLflow Tracking (30s)
"Tout est tracking dans MLflow."
[Ouvrir http://localhost:5000]
"Vous pouvez voir nos expériences d'embeddings, les métriques de retrieval,
et l'évolution de nos modèles."

### 3:00 - Conclusion
"C'est un prototype fonctionnel prêt pour être étendu avec des modèles
médicaux spécialisés comme BioBERT."

"Questions ?"
```

#### **Checklist Démo RAG**
- [ ] API FastAPI lancée et fonctionnelle
- [ ] Interface Streamlit accessible sur localhost:8501
- [ ] MLflow UI accessible sur localhost:5000
- [ ] Base de documents médicaux chargée (5+ documents)
- [ ] Query médicale de test prête ("diabetes symptoms")
- [ ] Retrieval fonctionne (<100ms)
- [ ] Chunks pertinents affichés avec scores
- [ ] MLflow runs visibles avec metrics
- [ ] Script démo répété 3+ fois
- [ ] Timing maîtrisé (<3 min total)

---

### **Étape 6 : Documentation Finale RAG**

#### **README.md Production-Ready**

```markdown
# Medical RAG Assistant

## Vue d'ensemble
Assistant IA médical basé sur Retrieval-Augmented Generation (RAG) pour aider les professionnels de santé à accéder rapidement à l'information médicale pertinente et sourcée.

## Quick Start
```bash
# Clone et installation
git clone https://github.com/omarchaara/medical-rag-assistant.git
cd medical-rag-assistant
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Exécution pipeline
python -m src.pipeline.pipeline

# API + Frontend
uvicorn src.api.main:app --reload
streamlit run src/frontend/app.py

# MLflow
mlflow ui
```

## Services
- **API FastAPI**: http://localhost:8000
- **Frontend Streamlit**: http://localhost:8501
- **MLflow UI**: http://localhost:5000

## Architecture RAG
```
Documents Médicaux (PDF/DOCX/TXT)
         ↓
   Ingestion & Chunking
         ↓
   Embedding (MiniLM-L6-v2)
         ↓
   Vector DB (ChromaDB)
         ↓
   Retrieval Sémantique
         ↓
   Réponses Contextuelles + Sources
```

## Stack Technique
- **Python 3.11+** + FastAPI
- **LangChain** + LangChain-Community
- **Sentence-Transformers** (MiniLM-L6-v2)
- **ChromaDB** (Vector Database)
- **MLflow** (Model Tracking)
- **Streamlit** (Frontend)
- **Prometheus + Grafana** (Monitoring)

## Résultats
- **MRR (Mean Reciprocal Rank)**: 1.000 (testing)
- **Retrieval Latency**: <50ms per query
- **Embedding Dimensions**: 384
- **Baselines**: TF-IDF, Random, MiniLM-L6-v2
- **5+ documents médicaux** traités

## Tests
```bash
# Tests unitaires
pytest tests/

# Tests E2E RAG
pytest tests/test_e2e_rag.py

# Tests avec coverage
pytest --cov=src --cov-report=html
```

## Monitoring
```bash
# Prometheus
docker-compose -f docker-compose.monitoring.yml up

# Grafana Dashboard
http://localhost:3000
```

## Troubleshooting
- **API port 8000 occupied?** Change uvicorn port
- **Embedding error?** Vérifier modèle téléchargé : `~/.cache/huggingface/`
- **Vector store empty?** Rechargez documents : `python -m src.pipeline.pipeline`
- **MLflow no runs?** Vérifiez : http://localhost:5000

## Améliorations Futures
- [ ] Intégration BioBERT/PubMedBERT spécialisés
- [ ] Support multi-modal (images médicales + texte)
- [ ] A/B testing de modèles d'embeddings
- [ ] API rate limiting et authentification
- [ ] Interface chat conversationnelle
- [ ] Citations et références médicales formelles

## Repository
- **GitHub**: https://github.com/omarchaara/medical-rag-assistant
- **Documentation**: docs/
- **Équipe**: Omar Chaara et al.
```

---

## 🎯 LIVRABLES ATTENDUS JOUR 5

### **TP 1 : Monitoring RAG**
- [ ] API instrumentée avec Prometheus (métriques RAG)
- [ ] `tests/test_e2e_rag.py` avec 5+ tests E2E
- [ ] Prometheus + Grafana configurés
- [ ] Dashboard Grafana RAG (latency, retrieval, MRR)

### **TP 2 : Présentation RAG**
- [ ] Slides (8 slides adaptées RAG)
- [ ] Script démo live RAG préparé
- [ ] README.md production-ready
- [ ] Présentation livrée (15 min)

---

## 📝 RÉSUMÉ JOUR 5 & PROJET COMPLET

✅ **Monitoring en place** (Prometheus + Grafana adaptés RAG)  
✅ **Tests E2E complets** (pipeline RAG testé bout-en-bout)  
✅ **Documentation finale** (README + ARCHITECTURE production-ready)  
✅ **Présentation** (slides RAG + démo live fonctionnelle)  
✅ **Projet complet** (Jours 1-5 : Infrastructure → Pipeline → Training → Production)

---

## 🚀 PROCHAINES ÉTAPES APRÈS JOUR 5

1. **Déploiement Production** : AWS/GCP/Docker
2. **Modèles Spécialisés** : BioBERT, PubMedBERT
3. **Interface Chat** : Conversation médicale continue
4. **Citations Médicales** : Références formelles et sources
5. **Multi-modal** : Images médicales + texte
6. **Scalability** : Traiter millions de documents

---

**Le projet Medical RAG Assistant est maintenant complet et prêt pour présentation !** 🏥🚀