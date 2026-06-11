# Jour 3 – Embeddings & Recherche Sémantique

## Objectif

Transformer les chunks médicaux générés au Jour 2 en représentations vectorielles afin de permettre une recherche sémantique performante dans le système RAG.

## Travaux réalisés

### 1. Génération des Embeddings

* Intégration d'un modèle d'embedding médical.
* Conversion de chaque chunk en vecteur numérique.
* Préparation des données pour l'indexation vectorielle.

### 2. Mise en place de ChromaDB

* Déploiement de la base vectorielle ChromaDB.
* Création d'une collection dédiée aux documents médicaux.
* Stockage des chunks et de leurs métadonnées.

### 3. Indexation des Documents

* Enregistrement des embeddings dans ChromaDB.
* Association de chaque vecteur à son chunk d'origine.
* Conservation des métadonnées pour la traçabilité.

### 4. Recherche Sémantique

* Implémentation d'un moteur de recherche par similarité.
* Calcul de la distance entre la question utilisateur et les embeddings stockés.
* Récupération des Top-K chunks les plus pertinents.

### 5. Validation du Pipeline RAG

* Test des requêtes médicales.
* Vérification de la pertinence des chunks retournés.
* Contrôle de la qualité du contexte récupéré avant génération de réponse.

## Résultat obtenu

Le système est désormais capable de :

* Transformer les documents médicaux en vecteurs.
* Stocker ces vecteurs dans ChromaDB.
* Rechercher les informations médicales pertinentes à partir d'une question utilisateur.
* Fournir le contexte nécessaire au futur modèle LLM.

## Préparation du Jour 4

Les données sont maintenant indexées et accessibles.

Le Jour 4 permettra :

* l'intégration d'Ollama,
* le déploiement du modèle Mistral 7B,
* la génération de réponses augmentées par récupération (RAG complet),
* l'exposition des services via FastAPI.
