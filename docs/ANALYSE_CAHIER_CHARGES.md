# Analyse du Cahier des Charges - Medical RAG Assistant

## 📋 Étape 1 : Lecture Active du Cahier des Charges

### 🔑 Question 1 : Quel problème résout-on ?

#### **Problème Principal**
**Accès rapide et fiable à l'information médicale scientifique pour les professionnels de santé**

#### **Contexte**
- Les professionnels de santé (médecins, infirmiers, étudiants en médecine) ont besoin de réponses basées sur des preuves scientifiques
- La littérature médicale explose (milliers d'articles par an)
- Google/Search généralistes ne sont pas assez spécifiques ou fiables
- Les guidelines cliniques changent fréquemment
- Le temps est critique en contexte médical

#### **Impact**
- **Qualité des soins** : Réponses basées sur des preuves scientifiques récentes
- **Efficiences** : Réponse en secondes vs heures de recherche manuelle
- **Formation** : Aide à l'apprentissage pour les étudiants
- **Sécurité patient** : Réduction des erreurs médicales par meilleure information
- **Coût** : Réduction des procédures inutiles par meilleure information

#### **Client Cible**
- **Primaire** : Professionnels de santé en exercice (médecins généralistes, spécialistes)
- **Secondaire** : Étudiants en médecine et paramédical
- **Tertiaire** : Chercheurs biomédicaux

---

### 🔑 Question 2 : Qui utilise ? Acteurs, Rôles, Permissions

#### **Utilisateur Principal : Professionnel de Santé**
**Profil** :
- Médecin généraliste ou spécialiste
- Infirmier de pratique avancée
- Étudiant en médecine (3ème cycle+)
- Pharmacien clinique

**Rôles** :
- Pose des questions médicales cliniques
- Consulte les réponses avec sources
- Peut donner du feedback sur la qualité

**Permissions** :
- ✅ Lire les réponses
- ✅ Voir les sources citées
- ✅ Donner du feedback (rating 1-5)
- ✅ Sauvegarder des questions/réponses favorites
- ❌ NE PEUT PAS modifier la base de connaissances

#### **Administrateur Système**
**Profil** :
- Administrateur IT ou Data Scientist
- Responsable de la maintenance

**Rôles** :
- Gère les documents sources
- Surveille la qualité du système
- Gère les utilisateurs

**Permissions** :
- ✅ Toutes les permissions utilisateur
- ✅ Ajouter/supprimer des documents
- ✅ Voir les analytics d'utilisation
- ✅ Gérer les utilisateurs
- ✅ Modifier la configuration

#### **Data Scientist / Chercheur**
**Profil** :
- Équipe de développement ou recherche
- Améliore le système

**Rôles** :
- Analyse les logs et feedback
- Améliore les modèles
- Expérimente nouvelles features

**Permissions** :
- ✅ Permissions utilisateur
- ✅ Accès aux logs bruts
- ✅ Accès MLflow pour expérimentations
- ❌ NE PEUT PAS modifier les données production

---

### 🔑 Question 3 : Quels sont les données entrantes ?

#### **Sources de Données**

##### **1. Littérature Scientifique (Primary)**
**Format** : PDF, HTML
**Sources** :
- PubMed Central (articles gratuits)
- Guidelines cliniques (OMS, HAS, NIH)
- Revues médicales (NEJM, Lancet, BMJ)
- Thèses et mémoires médicaux

**Volume Estimé** :
- Initial : 100-500 documents
- Cible 1 mois : 1,000-5,000 documents
- Cible 6 mois : 10,000-50,000 documents

**Structure** :
```
Document
├── Metadata (titre, auteurs, date, journal)
├── Abstract
├── Introduction
├── Méthodes
├── Résultats
├── Discussion
└── Références
```

##### **2. Guidelines Cliniques (Secondary)**
**Format** : PDF, HTML, parfois Word
**Sources** :
- Haute Autorité de Santé (HAS) - France
- National Institute for Health and Care Excellence (NICE) - UK
- World Health Organization (WHO)
- Sociétés savantes (cardiologie, pneumologie, etc.)

**Volume** : 50-200 guidelines (plus stables que la littérature)

##### **3. Questions Utilisateurs (Runtime)**
**Format** : Texte libre (français)
**Volume** :
- Test : 50-100 questions/jour
- Production : 1,000-10,000 questions/jour

**Exemples** :
- "Quels sont les symptômes de l'infarctus du myocarde ?"
- "Quel est le traitement de première ligne pour l'hypertension ?"
- "Quelles sont les contre-indications de l'aspirine ?"

##### **4. Feedback Utilisateurs (Runtime)**
**Format** : Structuré (rating 1-5, commentaire texte)
**Volume** : 10-20% des questions génèrent du feedback

---

### 🔑 Question 4 : Quels traitements à faire ?

#### **Pipeline de Traitement**

##### **Phase 1 : Ingestion des Documents**
**Traitement** :
1. **Téléchargement** : Récupération des documents depuis sources
2. **Parsing** : Extraction texte depuis PDF/HTML/DOCX
3. **Nettoyage** :
   - Suppression headers/footers
   - Normalisation espaces
   - Suppression références bibliographiques (si nécessaire)
4. **Chunking** : Division en segments de 512 tokens avec overlap de 50
5. **Metadata Extraction** : Récupération automatique (titre, auteurs, date)

##### **Phase 2 : Embedding Generation**
**Traitement** :
1. **Embedding par chunk** : Génération vecteurs avec BioBERT/sentence-transformers
2. **Normalisation** : Normalisation L2 des vecteurs
3. **Indexation** : Stockage dans ChromaDB avec metadata
4. **PostgreSQL Index** : Création index metadata pour recherche filtrée

##### **Phase 3 : Query Processing (Runtime)**
**Traitement** :
1. **Normalisation** : Nettoyage question utilisateur
2. **Embedding Query** : Génération vecteur pour la question
3. **Semantic Search** : Recherche similarity dans ChromaDB (top_k=5)
4. **Filtrage** : Filtrage par date, type de document, spécialité (optionnel)
5. **Re-ranking** : Réordonnement des résultats (optionnel)

##### **Phase 4 : Context Building**
**Traitement** :
1. **Concaténation** : Assemblage des chunks retrieved
2. **Context Formatting** : Formatage pour le LLM (avec sources)
3. **Prompt Engineering** : Construction du prompt médical

##### **Phase 5 : LLM Generation**
**Traitement** :
1. **Inference** : Génération réponse avec Mistral 7B via Ollama
2. **Citation** : Ajout des sources dans la réponse
3. **Confidence Score** : Calcul score de confiance (basé sur retrieval)
4. **Formatting** : JSON structuré pour l'API

##### **Phase 6 : Post-Processing**
**Traitement** :
1. **Validation** : Vérification cohérence réponse
2. **Formatting** : Mise en forme pour l'UI
3. **Logging** : Enregistrement query, réponse, temps, sources
4. **Feedback Collection** : Stockage feedback utilisateur

---

### 🔑 Question 5 : Quelles données sortantes ?

#### **1. Réponse à la Question Utilisateur**

**Format** : JSON
```json
{
  "answer": "Texte de la réponse générée",
  "sources": [
    {
      "title": "Titre de l'article",
      "authors": ["Auteur 1", "Auteur 2"],
      "journal": "Nom du journal",
      "year": 2023,
      "excerpt": "Extrait pertinent",
      "confidence": 0.85
    }
  ],
  "confidence_score": 0.82,
  "query_time_ms": 2450,
  "model_used": "mistral-7b",
  "timestamp": "2025-06-08T14:30:00Z"
}
```

**Affichage UI** :
- Réponse principale (paragraphe structuré)
- Sources citées avec liens cliquables
- Score de confiance
- Temps de réponse

#### **2. Métriques d'Utilisation (Monitoring)**

**Format** : Temps réel + Agrégations
```json
{
  "daily_stats": {
    "total_queries": 1234,
    "avg_response_time_ms": 2300,
    "avg_confidence_score": 0.78,
    "unique_users": 45
  },
  "top_queries": [
    {"query": "symptômes infarctus", "count": 23},
    {"query": "traitement hypertension", "count": 18}
  ]
}
```

#### **3. Logs d'Expérimentation (MLflow)**

**Format** : MLflow tracking
- Hyperparameters des modèles
- Métriques de performance
- Versions de modèles
- Comparaisons A/B testing

#### **4. Analytics de Feedback**

**Format** : Dashboard
- Rating moyen par type de question
- Questions avec low feedback
- Suggestions d'amélioration
- Corrélation confidence score vs rating utilisateur

---

### 🔑 Question 6 : Quelles sont les contraintes ?

#### **Contraintes de Performance**

##### **Latence**
- **Query End-to-End** : < 3 secondes (95th percentile)
  - Retrieval : < 500ms
  - LLM Generation : < 2 secondes
  - Formatting : < 500ms
- **Document Ingestion** : < 10 secondes/document
- **Startup Time** : < 30 secondes pour docker-compose up

##### **Throughput**
- **Concurrent Queries** : 10+ simultanés
- **QPS (Queries Per Second)** : 5-10 QPS sustained
- **Document Indexing** : 100+ documents/heure

##### **Accuracy**
- **Retrieval Precision** : > 0.85 (top_k=5 chunks pertinents)
- **Answer Quality** : > 4/5 (moyenne feedback utilisateurs)
- **Source Citation** : 100% (toujours afficher sources)

#### **Contraintes de Ressources**

##### **CPU**
- **Minimum** : 4 cores
- **Recommandé** : 8 cores
- **Allocation** :
  - Ingestion : 2-4 cores
  - API : 1-2 cores
  - LLM (CPU inference) : 4-8 cores

##### **RAM**
- **Minimum** : 16GB
- **Optimal** : 32GB
- **Allocation** :
  - ChromaDB : 2-4GB
  - PostgreSQL : 1-2GB
  - Ollama Mistral 7B : 4-8GB
  - API + Frontend : 1-2GB
  - OS + Overhead : 2-4GB

##### **Stockage**
- **Minimum** : 50GB
- **Allocation** :
  - Ollama models : ~4GB
  - ChromaDB vectors : 10-30GB (selon volume documents)
  - PostgreSQL : 1-5GB
  - Documents source : 10-20GB
  - Logs : 5-10GB

##### **GPU (Optionnel)**
- **Non obligatoire** mais fortement recommandé
- **Bénéfice** : 2-5x plus rapide pour LLM inference
- **Sans GPU** : CPU inference fonctionnel mais plus lent

#### **Contraintes de Sécurité & Privacy**

##### **Données Médicales**
- **Privacy** : Aucune donnée patient ne doit être stockée
- **Anonymisation** : Logs query anonymisés si possible
- **Local Only** : Aucun envoi de données à APIs externes
- **Compliance** : Respect RGPD (si applicable)

##### **Accès**
- **Authentication** : JWT tokens (implémentation future)
- **Authorization** : Role-based access control (RBAC)
- **Audit Trail** : Logging de toutes les actions sensibles

#### **Contraintes Budgétaires**

##### **Coûts**
- **Infrastructure** : 0€ (on-premise, Docker)
- **LLM** : 0€ (Ollama local)
- **Vector DB** : 0€ (ChromaDB open-source)
- **Total** : Coût matériel uniquement

##### **Maintenance**
- **Temps** : 2-4 heures/semaine pour maintenance
- **Mises à jour** : Mensuelles ( modèles, dependencies)

#### **Contraintes Temporelles (Projet)**

##### **Délai**
- **Durée totale** : 5 jours (semaine intensive)
- **Sprints** : 1 jour par sprint
- **Démo finale** : Jour 5 après-midi

##### **Livraison**
- **J1** : Infrastructure complète
- **J2** : Pipeline ingestion fonctionnel
- **J3** : Retrieval opérationnel
- **J4** : API + LLM intégrés
- **J5** : Frontend + Monitoring + Démo

#### **Contraintes Scalabilité**

##### **Évolutivité**
- **Court terme** : 10,000 documents, 100 utilisateurs
- **Moyen terme** : 100,000 documents, 1,000 utilisateurs
- **Long terme** : Architecture permet scaling horizontal (Kubernetes ready)

##### **Maintenance**
- **Code modulaire** : Facile à étendre
- **Documentation** : complète et à jour
- **Tests** : Couverture minimale 70%

#### **Contraintes Techniques**

##### **Stack**
- **Langage** : Python 3.11+
- **OS** : Linux/Windows/Mac compatible
- **Docker** : Version 20.10+
- **Python Packages** : Versions pinning dans requirements.txt

##### **Dépendances**
- **Internet** : Requis uniquement pour :
  - Initial setup (download images Docker)
  - Download models Ollama
  - Pull documents sources
- **Offline Capable** : Une fois initialisé, peut fonctionner offline

---

## 🎯 Synthèse de l'Analyse

### **Problème** : Accès rapide et fiable à l'information médicale scientifique

### **Solution** : Système RAG combinant :
- Retrieval sémantique avec embeddings médicaux
- LLM local pour génération de réponses
- Interface professionnelle pour utilisateurs médicaux

### **Utilisateurs** : Professionnels de santé (primaire), étudiants (secondaire)

### **Données** : Littérature scientifique + guidelines cliniques (100-50k documents)

### **Traitements** : Ingestion → Embedding → Retrieval → Generation → Formatting

### **Sorties** : Réponses avec sources, métriques, analytics

### **Contraintes** :
- Performance : <3s/query
- Resources : 16GB RAM min, 4 cores CPU
- Budget : 0€ (open-source)
- Privacy : 100% local
- Délai : 5 jours MVP

---

## ✅ Checklist Validation Cahier des Charges

- [x] Problème clairement identifié et justifié
- [x] Utilisateurs définis avec rôles et permissions
- [x] Sources de données identifiées avec volumes estimés
- [x] Pipeline de traitement détaillé
- [x] Sorties spécifiées avec formats
- [x] Contraintes performance documentées
- [x] Contraintes ressources définies
- [x] Contraintes sécurité considérées
- [x] Contraintes budgétaires établies
- [x] Contraintes temporelles réalistes

## 🚀 Prêt pour Étape 2 : Modélisation de l'Architecture

Cette analyse complète nous permet maintenant de modéliser l'architecture technique du système avec une compréhension précise des besoins, contraintes et objectifs.
