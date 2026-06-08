# Sprint Planning - Medical RAG Assistant

## Vue d'ensemble

Projet de 5 jours avec méthodologie Agile. Chaque jour = 1 sprint avec objectifs clairs, livrables et définition du "Done".

## Backlog Produit

### Epic 1: Data Pipeline & Ingestion
**Story 1.1**: Document Loading System
- **En tant que** système
- **Je veux** charger des documents médicaux (PDF, DOCX)
- **Afin de** les indexer pour recherche sémantique
- **Acceptance Criteria**:
  - ✓ Support PDF parsing
  - ✓ Support DOCX parsing
  - ✓ Extraction text + metadata
  - ✓ Gestion erreurs fichiers corrompus
- **Estimation** : 4 heures

**Story 1.2**: Text Chunking Strategy
- **En tant que** système
- **Je veux** diviser les documents en chunks
- **Afin de** créer des unités de recherche optimales
- **Acceptance Criteria**:
  - ✓ Chunk size configurable (default 512)
  - ✓ Overlap configurable (default 50)
  - ✓ Préservation metadata par chunk
  - ✓ Boundary respect (phrases, paragraphes)
- **Estimation** : 3 heures

**Story 1.3**: BioBERT Embeddings Generation
- **En tant que** système
- **Je veux** générer des embeddings médicaux
- **Afin de** capturer la sémantique biomédicale
- **Acceptance Criteria**:
  - ✓ Intégration sentence-transformers
  - ✓ Modèle BioBERT/all-MiniLM-L6-v2
  - ✓ Batch processing efficace
  - ✓ Cache des embeddings
- **Estimation** : 4 heures

**Story 1.4**: Vector Store Indexing
- **En tant que** système
- **Je veux** stocker les embeddings dans ChromaDB
- **Afin de** permettre recherche sémantique rapide
- **Acceptance Criteria**:
  - ✓ Connection ChromaDB fonctionnelle
  - ✓ Création collections
  - ✓ Insertion embeddings + metadata
  - ✓ Gestion duplicates
- **Estimation** : 3 heures

### Epic 2: RAG Pipeline & Retrieval
**Story 2.1**: LangChain Retrieval Chain
- **En tant que** système
- **Je veux** implémenter une chaîne de retrieval
- **Afin de** trouver les chunks les plus pertinents
- **Acceptance Criteria**:
  - ✓ LangChain Retriever configuré
  - ✓ Similarity search top_k=5
  - ✓ Score threshold configurable
  - ✓ Context building optimal
- **Estimation** : 4 heures

**Story 2.2**: Query Preprocessing
- **En tant que** système
- **Je veux** prétraiter les questions utilisateurs
- **Afin d'améliorer la qualité de retrieval
- **Acceptance Criteria**:
  - ✓ Normalization text
  - ✓ Query expansion (optionnel)
  - ✓ Medical term detection
  - ✓ Validation input
- **Estimation** : 2 heures

**Story 2.3**: Retrieval Optimization
- **En tant que** système
- **Je veux** optimiser les paramètres de recherche
- **Afin de** maximiser la relevance des résultats
- **Acceptance Criteria**:
  - ✓ A/B testing top_k values
  - ✓ Tuning similarity threshold
  - ✓ Hybrid search (keyword + semantic)
  - **Estimation** : 3 heures

### Epic 3: LLM Integration & Generation
**Story 3.1**: Ollama Setup
- **En tant que** développeur
- **Je veux** configurer Ollama avec Mistral 7B
- **Afin de** générer des réponses médicales
- **Acceptance Criteria**:
  - ✓ Ollama service opérationnel
  - ✓ Mistral 7B téléchargé
  - ✓ API Ollama fonctionnelle
  - ✓ Test generation basique
- **Estimation** : 2 heures

**Story 3.2**: Generation Chain
- **En tant que** système
- **Je veux** créer une chaîne de génération LangChain
- **Afin de** générer des réponses contextuelles
- **Acceptance Criteria**:
  - ✓ Prompt template médical
  - ✓ Context injection depuis retrieval
  - **Estimation** : 4 heures

**Story 3.3**: Response Formatting
- **En tant que** système
- **Je veux** formater les réponses avec sources
- **Afin de** fournir la traçabilité
- **Acceptance Criteria**:
  - ✓ Inclusion sources citées
  - ✓ Confidence score
  - ✓ Structuration JSON
  - **Estimation** : 2 heures

### Epic 4: API Development
**Story 4.1**: FastAPI Setup
- **En tant que** développeur
- **Je veux** configurer FastAPI
- **Afin de** créer des endpoints REST
- **Acceptance Criteria**:
  - ✓ FastAPI application créée
  - ✓ CORS configuré
  - ✓ Documentation auto (/docs)
  - ✓ Validation Pydantic
- **Estimation** : 2 heures

**Story 4.2**: Query Endpoint
- **En tant que** client API
- **Je veux** envoyer une question
- **Afin d'obtenir une réponse RAG
- **Acceptance Criteria**:
  - ✓ POST /api/query
  - ✓ Request validation
  - ✓ Response structurée
  - ✓ Error handling
- **Estimation** : 3 heures

**Story 4.3**: Ingestion Endpoint
- **En tant que** admin système
- **Je veux** ingérer de nouveaux documents
- **Afin d'élargir la base de connaissances
- **Acceptance Criteria**:
  - ✓ POST /api/ingest
  - ✓ File upload support
  - ✓ Async processing
  - ✓ Status tracking
- **Estimation** : 3 heures

**Story 4.4**: Health & Admin Endpoints
- **En tant que** ops
- **Je veux** vérifier l'état du système
- **Afin de** monitoring
- **Acceptance Criteria**:
  - ✓ GET /api/health
  - ✓ GET /api/sources
  - ✓ GET /api/stats
- **Estimation** : 1 heure

### Epic 5: Frontend Development
**Story 5.1**: Streamlit Setup
- **En tant que** développeur
- **Je veux** créer une interface Streamlit
- **Afin d'interagir avec le système
- **Acceptance Criteria**:
  - ✓ Streamlit app créée
  - ✓ Connection API
  - ✓ Layout basique
- **Estimation** : 2 heures

**Story 5.2**: Query Interface
- **En tant que** utilisateur médical
- **Je veux** poser des questions
- **Afin d'obtenir des réponses
- **Acceptance Criteria**:
  - ✓ Input field question
  - ✓ Display réponse
  - ✓ Display sources
  - ✓ Chat history
- **Estimation** : 3 heures

**Story 5.3**: Admin Interface
- **En tant que** admin
- **Je veux** gérer les documents
- **Afin de** mettre à jour la base
- **Acceptance Criteria**:
  - ✓ File upload interface
  - ✓ Document list
  - ✓ Delete functionality
- **Estimation** : 2 heures

### Epic 6: Monitoring & Documentation
**Story 6.1**: MLflow Integration
- **En tant que** data scientist
- **Je veux** tracker les expérimentations
- **Afin de** monitor les performances
- **Acceptance Criteria**:
  - ✓ MLflow server setup
  - ✓ Tracking queries/responses
  - ✓ Metrics logging
- **Estimation** : 2 heures

**Story 6.2**: Feedback Mechanism
- **En tant que** utilisateur
- **Je veux** noter les réponses
- **Afin d'améliorer le système
- **Acceptance Criteria**:
  - ✓ Rating 1-5 stars
  - ✓ Comment optionnel
  - ✓ Stockage feedback
- **Estimation** : 2 heures

**Story 6.3**: Documentation Technique
- **En tant que** développeur
- **Je veux** documenter le système
- **Afin de** faciliter la maintenance
- **Acceptance Criteria**:
  - ✓ API documentation
  - ✓ Setup guide
  - ✓ Architecture diagrams
  - ✓ Deployment guide
- **Estimation** : 3 heures

## Sprint Breakdown

### SPRINT 1 (J1) - Infrastructure ✅
**Objectif** : Setup infrastructure de base
**Stories** :
- ✅ Architecture documentée
- ✅ Docker Compose avec 6 services
- ✅ Git repository initialisé
- ✅ .gitignore configuré
- ✅ ARCHITECTURE.md créée
**Status** : COMPLETED

### SPRINT 2 (J2) - Data Pipeline & Ingestion
**Objectif** : Implémenter pipeline d'ingestion de documents
**Stories** :
- Story 1.1: Document Loading System (4h)
- Story 1.2: Text Chunking Strategy (3h)
- Story 1.3: BioBERT Embeddings Generation (4h)
- Story 1.4: Vector Store Indexing (3h)
**Total Estimation** : 14 heures
**Livrables** :
- Pipeline ingestion fonctionnel
- Documents sample indexés dans ChromaDB
- Tests unitaires ingestion
**Définition Done** :
- ✅ Tous services ingestion testés manuellement
- ✅ Au moins 10 documents indexés
- ✅ Embeddings générés et stockés
- ✅ Code commité avec tests

### SPRINT 3 (J3) - RAG Pipeline & Retrieval
**Objectif** : Implémenter chaîne RAG avec retrieval sémantique
**Stories** :
- Story 2.1: LangChain Retrieval Chain (4h)
- Story 2.2: Query Preprocessing (2h)
- Story 2.3: Retrieval Optimization (3h)
**Total Estimation** : 9 heures
**Livrables** :
- RAG chain fonctionnelle
- Retrieval testé avec queries sample
- Métriques de relevance calculées
**Définition Done** :
- ✅ Retrieval fonctionne sur 5+ queries test
- ✅ Top-k chunks pertinents (validation manuelle)
- ✅ Latence <500ms pour retrieval
- ✅ Code commité avec tests

### SPRINT 4 (J4) - LLM Integration & API
**Objectif** : Intégrer LLM et créer API REST
**Stories** :
- Story 3.1: Ollama Setup (2h)
- Story 3.2: Generation Chain (4h)
- Story 3.3: Response Formatting (2h)
- Story 4.1: FastAPI Setup (2h)
- Story 4.2: Query Endpoint (3h)
- Story 4.3: Ingestion Endpoint (3h)
- Story 4.4: Health & Admin Endpoints (1h)
**Total Estimation** : 17 heures
**Livrables** :
- Ollama Mistral 7B opérationnel
- FastAPI avec endpoints complets
- End-to-end RAG fonctionnel
**Définition Done** :
- ✅ Query end-to-end fonctionne (<3s)
- ✅ Réponses avec sources affichées
- ✅ API testée via Swagger UI
- ✅ Documentation API complète

### SPRINT 5 (J5) - Frontend & Monitoring
**Objectif** : Créer interface utilisateur et monitoring
**Stories** :
- Story 5.1: Streamlit Setup (2h)
- Story 5.2: Query Interface (3h)
- Story 5.3: Admin Interface (2h)
- Story 6.1: MLflow Integration (2h)
- Story 6.2: Feedback Mechanism (2h)
- Story 6.3: Documentation Technique (3h)
**Total Estimation** : 14 heures
**Livrables** :
- Streamlit UI fonctionnelle
- MLflow tracking actif
- Documentation complète
- Démo finale
**Définition Done** :
- ✅ Interface utilisateur testable
- ✅ Feedback mechanism fonctionnel
- ✅ Documentation technique complète
- ✅ Démo prête pour présentation

## Task Assignment Template

### Équipe Membres (A remplir)
- **Member 1** : Spécialité [Backend/Data]
- **Member 2** : Spécialité [ML/RAG]
- **Member 3** : Spécialité [Frontend/DevOps]

### Assignment Recommandé
**J2 (Data Pipeline)** :
- Member 1 : Document Loading + Chunking
- Member 2 : Embeddings Generation
- Member 3 : Vector Store Indexing

**J3 (RAG Pipeline)** :
- Member 1 : LangChain Retrieval Chain
- Member 2 : Query Preprocessing + Optimization
- Member 3 : Tests + Validation

**J4 (LLM + API)** :
- Member 1 : FastAPI Setup + Endpoints
- Member 2 : Ollama + Generation Chain
- Member 3 : Response Formatting + Tests

**J5 (Frontend + Monitoring)** :
- Member 1 : MLflow Integration + Documentation
- Member 2 : Feedback Mechanism
- Member 3 : Streamlit UI complète

## Daily Standup Format

### Matin (9h00 - 9h15)
**Format** : 15 min standup
**Questions** :
1. Qu'est-ce que j'ai fait hier ?
2. Qu'est-ce que je vais faire aujourd'hui ?
3. Quels sont mes blockers ?

### Soir (17h00 - 17h30)
**Format** : Sprint Review
**Questions** :
1. Qu'est-ce qu'on a fini aujourd'hui ?
2. Démo des fonctionnalités
3. Lessons learned
4. Plan pour demain

## Definition of Done (DoD)

### Pour chaque Story
- ✅ Code implémenté et fonctionnel
- ✅ Tests unitaires passent
- ✅ Code reviewé par au moins 1 personne
- ✅ Commit message explicite
- ✅ Documentation mise à jour (si nécessaire)
- ✅ Pas de console warnings/errors

### Pour chaque Sprint
- ✅ Toutes stories terminées selon DoD story
- ✅ Tests d'intégration passent
- ✅ Démo fonctionnelle
- ✅ Retro sprint effectuée
- ✅ Backlog sprint suivant prêt

## Risk Management

### Risques Identifiés
1. **Performance Ollama CPU** : LLM inference lent sans GPU
   - *Mitigation* : Optimiser prompt, réduire context, chunk size
2. **ChromaDB Memory** : Memory leak avec gros volumes
   - *Mitigation* : Monitoring RAM, pagination queries
3. **BioBERT Model Size** : Modèle trop lourd pour ressources
   - *Mitigation* : Utiliser all-MiniLM-L6-v2 (plus léger)
4. **Docker Volumes** : Problèmes permissions Windows
   - *Mitigation* : Tester cross-platform early
5. **Integration Ollama-LangChain** : Compatibility issues
   - *Mitigation* : Version pinning requirements.txt

### Contingency Plan
- Si J2 non fini : Reprioritizer J3 (skip optimization)
- Si J4 non fini : Simplifier API (endpoints minimaux)
- Si J5 non fini : Frontend basique sans admin

## Success Metrics

### Techniques
- ✅ docker compose up sans erreur
- ✅ Query latency <3s (95th percentile)
- ✅ Retrieval precision >0.85
- ✅ Tous tests passent

### Business
- ✅ Interface utilisateur intuitive
- ✅ Réponses médicalement pertinentes
- ✅ Sources toujours citées
- ✅ Système démontrable en 5 min

## Git Workflow

### Branch Strategy
- `main` : Production stable
- `develop` : Integration branch
- `feature/*` : Nouvelles fonctionnalités
- `bugfix/*` : Corrections bugs
- `hotfix/*` : Corrections urgentes prod

### Commit Convention
```
feat(scope): description
fix(scope): description
docs(scope): description
test(scope): description
refactor(scope): description
```

### Exemples
```
feat(ingestion): add PDF document loader
fix(api): resolve CORS issue
docs(readme): update setup instructions
test(retrieval): add similarity search tests
```

## Tools & Communication

### Collaboration
- **Git** : Version control
- **GitHub/GitLab** : Code review, issues
- **Discord/Slack** : Communication équipe
- **Trello/Jira** : Task tracking (optionnel)

### Documentation
- **ARCHITECTURE.md** : Design decisions
- **SPRINT_PLANNING.md** : Ce document
- **API.md** : API endpoints (J4)
- **SETUP.md** : Installation guide (J5)

## Timeline Summary

| Jour | Sprint | Focus | Estimation |
|------|--------|-------|------------|
| J1 | Infrastructure | Docker, Git, Architecture | ✅ Done |
| J2 | Data Pipeline | Ingestion, Embeddings, ChromaDB | 14h |
| J3 | RAG Pipeline | Retrieval, LangChain, Optimization | 9h |
| J4 | LLM + API | Ollama, FastAPI, Endpoints | 17h |
| J5 | Frontend + Monitoring | Streamlit, MLflow, Docs | 14h |

**Total** : 68 heures sur 5 jours (13.6h/jour pour équipe de 3-4 personnes)

## Notes pour Formateur

### Points de Validation J1
- ✅ Docker Compose structure correcte
- ✅ Services inter-connectables
- ✅ Architecture réaliste pour 5 jours
- ✅ Git workflow configuré

### Points de Validation J2
- Pipeline ingestion fonctionnel
- Documents indexés testables
- Performance embeddings acceptable

### Points de Validation J3
- Retrieval qualité suffisante
- Latence acceptable
- RAG chain intégrée

### Points de Validation J4
- API complète et documentée
- LLM generation fonctionnelle
- End-to-end test réussi

### Points de Validation J5
- Interface utilisateur utilisable
- Monitoring actif
- Documentation complète
- Démo impressionnante
