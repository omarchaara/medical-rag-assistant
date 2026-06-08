# Guide de Collaboration - Medical RAG Assistant

## 🚀 Setup Initial pour chaque membre

### 1. Cloner le repository
```bash
git clone https://github.com/<USERNAME_REPO>/medical-rag-assistant.git
cd medical-rag-assistant
```

### 2. Configurer Git
```bash
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Démarrer Docker
```bash
docker-compose up -d
```

## 🌿 Branch Strategy

### Branches principales
- `main` : Production stable (seulement merges validés)
- `develop` : Branch d'intégration (optionnelle)

### Branches de travail
- `feature/*` : Nouvelles fonctionnalités
- `bugfix/*` : Corrections de bugs
- `hotfix/*` : Corrections urgentes

### Workflow recommandé

```bash
# 1. Mettre à jour main
git checkout main
git pull origin main

# 2. Créer une branche de travail
git checkout -b feature/nom-fonctionnalite

# 3. Travailler et committer
git add .
git commit -m "feat(scope): description de la modification"

# 4. Pousser la branche
git push origin feature/nom-fonctionnalite

# 5. Créer une Pull Request sur GitHub
# - Aller sur le repository GitHub
# - Cliquer sur "Pull Requests" → "New Pull Request"
# - Sélectionner votre branche
# - Remplir le template de PR
# - Demander une review

# 6. Après validation, merger dans main
# - Via l'interface GitHub avec "Squash and merge"
```

## 📝 Conventions de Commit

### Format
```
type(scope): description

# Types autorisés
feat:     Nouvelle fonctionnalité
fix:      Correction de bug
docs:     Documentation only
style:    Formatting, missing semi colons, etc (no code change)
refactor: Code change that neither fixes a bug nor adds a feature
test:     Adding missing tests
chore:    Changes to the build process or auxiliary tools
```

### Exemples
```bash
git commit -m "feat(ingestion): add PDF document loader"
git commit -m "fix(api): resolve CORS issue"
git commit -m "docs(readme): update setup instructions"
git commit -m "test(retrieval): add similarity search tests"
```

## 🔄 Mise à jour fréquente

### Avant de commencer à travailler
```bash
git checkout main
git pull origin main
```

### Si des conflits surviennent
```bash
git pull origin main --rebase
# Résoudre les conflits manuellement
git add .
git rebase --continue
git push origin feature/ma-branche --force-with-lease
```

## 🚫 Règles importantes

1. **NE JAMAIS** commiter directement sur `main`
2. **TOUJOURS** créer une branche par feature
3. **TOUJOURS** pull avant de push
4. **JAMAIS** de `git push --force` (sauf `--force-with-lease`)
5. **TOUJOURS** écrire des messages de commit clairs
6. **TOUJOURS** demander une review avant de merger

## 📅 Daily Workflow

### Matin (9h00)
```bash
# Pull les derniers changements
git checkout main
git pull origin main

# Créer/mettre à jour votre branche
git checkout -b feature/tache-du-jour
# ou
git checkout feature/tache-en-cours
git pull origin main --rebase
```

### Soir (17h00)
```bash
# Committer et pusher
git add .
git commit -m "wip: progress sur la tache"
git push origin feature/tache-en-cours
```

## 🤝 Code Review Process

1. Créer une Pull Request
2. Remplir le template avec :
   - Description des changements
   - Tests effectués
   - Screenshot/Logs si applicable
3. Assigner au moins 1 reviewer
4. Attendre la validation
5. Corriger les commentaires si nécessaires
6. Merger après approval (Squash and merge)

## 🐛 Gestion des Conflits

### Quand un conflit survient
```bash
# 1. Identifier les fichiers en conflit
git status

# 2. Ouvrir les fichiers et chercher "<<<<<<< HEAD"
# 3. Résoudre manuellement les conflits
# 4. Marquer comme résolu
git add fichier-en-conflit.py

# 5. Continuer le rebase/merge
git rebase --continue
# ou
git commit

# 6. Pousser
git push origin feature/ma-branche
```

## 📊 Assignation des tâches

### J2 - Data Pipeline
- Member A : Document Loading + Chunking
- Member B : Embeddings Generation  
- Member C : Vector Store Indexing

### J3 - RAG Pipeline
- Member A : LangChain Retrieval Chain
- Member B : Query Preprocessing + Optimization
- Member C : Tests + Validation

### J4 - LLM + API
- Member A : FastAPI Setup + Endpoints
- Member B : Ollama + Generation Chain
- Member C : Response Formatting + Tests

### J5 - Frontend + Monitoring
- Member A : MLflow Integration + Documentation
- Member B : Feedback Mechanism
- Member C : Streamlit UI complète

## 🆘 En cas de problème

### Si quelque chose ne fonctionne pas
```bash
# Annuler les changements locaux
git checkout -- fichier.py

# Annuler le dernier commit (garder les changements)
git reset --soft HEAD~1

# Annuler le dernier commit (supprimer les changements)
git reset --hard HEAD~1

# Voir l'historique
git log --oneline --graph --all
```

### Demander de l'aide
- Demander à un coéquipier de review votre code
- Créer une issue sur GitHub pour blocker
- Communiquer sur Discord/Slack/Teams

## 📱 Communication

### Canaux recommandés
- **Discord/Slack** : Communication rapide
- **GitHub Issues** : Suivi des bugs et features
- **GitHub Pull Requests** : Code review
- **GitHub Discussions** : Questions techniques

### Daily Standup (9h00-9h15)
- Qu'est-ce que j'ai fait hier ?
- Qu'est-ce que je vais faire aujourd'hui ?
- Quels sont mes blockers ?

## ✅ Definition of Done

Avant de merger une PR :
- [ ] Code fonctionnel et testé
- [ ] Tests unitaires passent
- [ ] Code reviewé par au moins 1 personne
- [ ] Commit message explicite
- [ ] Documentation mise à jour (si nécessaire)
- [ ] Pas de console warnings/errors
- [ ] Docker compose up fonctionne

## 🎯 Conseils pour travailler efficacement

1. **Commitez souvent** : Petits commits fréquents > gros commits rares
2. **Communiquez** : Prévenez quand vous travaillez sur les mêmes fichiers
3. **Testez localement** : Ne pushz pas du code cassé
4. **Respectez les conventions** : Suivez les règles établies
5. **Demandez de l'aide** : Ne bloquez pas 2h sur un problème

## 📚 Ressources utiles

- [GitHub Documentation](https://docs.github.com)
- [Git Cheatsheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Effective Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)

## 🎓 Pour ce projet spécifique

- Priorité aux fonctionnalités critiques du sprint en cours
- Si vous finissez votre tâche, aidez un coéquipier
- Documentez vos découvertes techniques dans le dossier `docs/`
- Gardez un œil sur le `SPRINT_PLANNING.md` pour les priorités
