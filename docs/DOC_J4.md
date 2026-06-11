# Jour 4 – Déploiement & Interface Utilisateur

## Objectif

Transformer le moteur RAG développé lors des jours précédents en une application utilisable par un utilisateur final grâce à une API REST et une interface web interactive.

## Travaux réalisés

### 1. Développement de l'API FastAPI

* Création d'une API REST pour exposer les fonctionnalités du système RAG.
* Mise en place des endpoints :

  * `/health`
  * `/query`
  * `/documents`
* Validation des entrées avec Pydantic.
* Gestion des erreurs et des réponses JSON.

### 2. Intégration du moteur RAG

* Connexion entre FastAPI et ChromaDB.
* Recherche sémantique des chunks pertinents.
* Envoi du contexte récupéré au modèle LLM via Ollama.
* Génération de réponses médicales augmentées par récupération (RAG).

### 3. Développement de l'interface Streamlit

* Création d'un tableau de bord interactif.
* Zone de saisie des questions médicales.
* Affichage des réponses générées.
* Visualisation des documents et sources utilisées.

### 4. Tests et Validation

* Tests des endpoints FastAPI.
* Vérification de la communication :

  * Streamlit → API
  * API → ChromaDB
  * API → Ollama
* Validation du flux complet utilisateur.

### 5. Conteneurisation

* Intégration des services dans Docker Compose :

  * FastAPI
  * Streamlit
  * ChromaDB
  * PostgreSQL
  * Ollama
  * MLflow

## Résultat obtenu

Le système est désormais capable de :

* Recevoir une question utilisateur.
* Rechercher les informations médicales pertinentes dans ChromaDB.
* Générer une réponse grâce au modèle LLM.
* Afficher les résultats dans une interface web intuitive.

## Préparation du Jour 5

Le Jour 5 sera consacré à :

* l'optimisation des performances,
* la surveillance avec MLflow,
* les tests finaux,
* la documentation complète,
* la préparation de la démonstration et du pitch du MVP.
