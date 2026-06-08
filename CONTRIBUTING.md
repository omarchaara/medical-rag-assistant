# Guide pour Contributeurs - Medical RAG Assistant

Merci de votre intérêt pour contribuer au projet Medical RAG Assistant !

## 🚀 Comment Commencer

### 1. Fork le Repository
- Cliquez sur le bouton "Fork" en haut à droite de la page GitHub
- Cela créera une copie du repository dans votre compte GitHub

### 2. Clonez votre Fork
```bash
git clone https://github.com/VOTRE_USERNAME/medical-rag-assistant.git
cd medical-rag-assistant
```

### 3. Configurez l'Upstream
```bash
git remote add upstream https://github.com/USERNAME_ORIGINAL/medical-rag-assistant.git
git remote -v
```

### 4. Installez les Dépendances
```bash
pip install -r requirements.txt
```

## 🌿 Workflow de Développement

### Étape 1 : Synchroniser avec l'Upstream
```bash
git checkout main
git fetch upstream
git merge upstream/main
```

### Étape 2 : Créer une Branche
```bash
git checkout -b feature/nom-de-votre-feature
```

### Étape 3 : Faire vos Changements
```bash
# Travailler sur vos fichiers
git add .
git commit -m "feat(scope): description de vos changements"
```

### Étape 4 : Pousser vers votre Fork
```bash
git push origin feature/nom-de-votre-feature
```

### Étape 5 : Créer une Pull Request
- Allez sur votre repository GitHub
- Cliquez sur "Pull Requests" → "New Pull Request"
- Sélectionnez votre branche
- Remplissez le template PR
- Cliquez sur "Create Pull Request"

## 📝 Conventions de Code

### Python
- Suivez PEP 8
- Utilisez des type hints
- Documentez avec docstrings
- Limitez les lignes à 100 caractères

### Exemple
```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

def process_documents(file_paths: List[str], chunk_size: int = 512) -> Optional[List[str]]:
    """
    Process documents and return text chunks.
    
    Args:
        file_paths: List of file paths to process
        chunk_size: Size of text chunks (default: 512)
        
    Returns:
        List of text chunks or None if error
    """
    try:
        logger.info(f"Processing {len(file_paths)} documents")
        # Implementation
        return chunks
    except Exception as e:
        logger.error(f"Error processing documents: {e}")
        return None
```

### Git Messages
```
type(scope): description

Types: feat, fix, docs, style, refactor, test, chore
```

## 🧪 Tests

### Exécuter les Tests
```bash
pytest tests/
pytest tests/ -v  # Verbose
pytest tests/ --coverage  # With coverage
```

### Écrire des Tests
```python
import pytest

def test_document_loading():
    """Test document loading functionality"""
    # Arrange
    file_path = "test_document.pdf"
    
    # Act
    result = load_document(file_path)
    
    # Assert
    assert result is not None
    assert len(result.text) > 0
```

## 🐛 Signaler des Bugs

### Ouvrir une Issue
1. Allez sur "Issues" → "New Issue"
2. Utilisez le template "Bug Report"
3. Décrivez le bug avec :
   - Titre clair
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment (OS, Python version, etc.)
   - Screenshots/Logs

## 💡 Proposer des Features

### Ouvrir une Issue pour Feature
1. Allez sur "Issues" → "New Issue"
2. Utilisez le template "Feature Request"
3. Décrivez la feature avec :
   - Pourquoi cette feature est utile
   - Comment vous imaginez l'implémentation
   - Alternatives considérées

## 📚 Documentation

### Mettre à jour la Documentation
- README.md pour les changements utilisateur
- docs/ARCHITECTURE.md pour les changements d'architecture
- docs/SPRINT_PLANNING.md pour les changements de planning
- Ajoutez des docstrings dans le code

## 🤝 Code Review

### Pendant la Review
- Soyez constructif et respectueux
- Expliquez pourquoi vous suggérez des changements
- Acceptez les feedbacks avec ouverture d'esprit
- Posez des questions si vous ne comprenez pas

### Répondre aux Commentaires
- Répondez à tous les commentaires
- Expliquez les changements que vous avez faits
- Si vous n'êtes pas d'accord, expliquez pourquoi calmement

## 🚫 Ce qu'il faut éviter

- [ ] Commits massifs (faites des petits commits fréquents)
- [ ] Code sans tests
- [ ] Documentation obsolète
- [ ] Hardcoding de valeurs sensibles
- [ ] Ignorer les warnings et erreurs
- [ ] Commits directement sur main

## ✅ Avant de Soumettre une PR

- [ ] Code testé localement
- [ ] Tests passent
- [ ] Documentation mise à jour
- [ ] Pas de merge conflicts
- [ ] PR description complète
- [ ] Assignée pour review

## 🎯 Priorités du Projet

Actuellement, nous priorisons :
1. **Day 2** : Data Pipeline & Ingestion
2. **Day 3** : RAG Pipeline & Retrieval
3. **Day 4** : LLM Integration & API
4. **Day 5** : Frontend & Monitoring

Vérifiez `docs/SPRINT_PLANNING.md` pour les détails.

## 📞 Contact

Pour toute question :
- Ouvrez une GitHub Discussion
- Contactez l'équipe via Discord/Slack
- Posez une question lors du daily standup

## 📜 License

Ce projet est éducatif. En contribuant, vous acceptez que votre code soit utilisé dans ce cadre académique.

---

Merci de contribuer ! 🎉
