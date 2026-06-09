# Jour 2 – Data Pipeline & Processing

## Objectif

Mettre en place une pipeline ETL permettant d'ingérer, nettoyer, transformer et préparer des documents médicaux pour un futur système RAG.

## Travaux réalisés

### 1. Ingestion des données

* Création d'un chargeur de documents PDF (`MedicalDocumentLoader`).
* Détection automatique des fichiers présents dans `data/raw/`.

### 2. Extraction du contenu

* Mise en place d'un extracteur PDF (`PDFExtractor`).
* Conversion des documents PDF en texte exploitable.

### 3. Validation et nettoyage

* Validation de la qualité des données extraites.
* Nettoyage du texte (suppression des caractères inutiles, normalisation).

### 4. Enrichissement des métadonnées

* Génération des métadonnées :

  * Nom du document
  * Taille du texte
  * Nombre de mots
  * Date de traitement

### 5. Chunking intelligent

* Développement d'un `MedicalTextChunker`.
* Découpage du texte en chunks adaptés au RAG.
* Ajout de métadonnées par chunk (identifiant, type médical, score qualité, longueur).

### 6. Tests de la pipeline

* Intégration d'un document PDF médical de test.
* Vérification complète du flux :
  PDF → Extraction → Nettoyage → Chunking → Métadonnées.

## Résultat obtenu

Pipeline fonctionnelle capable de :

* Charger un document PDF médical.
* Extraire son contenu textuel.
* Générer les métadonnées.
* Produire des chunks exploitables pour la vectorisation future.

### Exemple de sortie

* Document : `medical_test_document.pdf`
* Taille du texte : 856 caractères
* Nombre de mots : 113
* Chunks générés : 1

## Préparation du Jour 3

Les données sont désormais prêtes pour :

* La génération d'embeddings.
* L'intégration de ChromaDB.
* L'indexation vectorielle.
* La recherche sémantique RAG.
