# 🎬 SCRIPT DÉMO LIVE RAG - 3 MINUTES

## SCÉNARIO DÉMO LIVE COMPLET (3 MINUTES)

---

## 📋 PRÉPARATION AVANT PRÉSENTATION

### **Checklist Pré-Démo:**
```bash
# Vérifier que tous les services sont lancés
✓ API FastAPI: http://localhost:8000
✓ Streamlit: http://localhost:8501  
✓ MLflow UI: http://localhost:5000
✓ Documents chargés (5+ documents médicaux)
✓ Query médicale de test préparée
✓ Backup local disponible (si WiFi défaille)
```

### **Recommandations:**
- Lancer tous les services 30 minutes avant présentation
- Avoir un script de backup si Streamlit ne fonctionne pas
- Préparer des screenshots en cas de problème
- Pratiquer le scénario 5+ fois avant présentation

---

## 🎯 SCÉNARIO DÉMO STEP-BY-STEP

### **0:00 - INTRODUCTION (30 secondes)**

**Speaker Script:**
```
"Bonjour, je vais maintenant vous faire une démonstration live de notre 
Medical RAG Assistant. Je vais montrer comment le pipeline RAG fonctionne 
en temps réel pour répondre à une question médicale."
```

**Actions:**
1. Ouvrir le terminal avec les services déjà lancés
2. Montrer que 3 terminaux sont actifs (API, Streamlit, MLflow)
3. Ouvrir le navigateur sur http://localhost:8501

---

### **0:30 - PRÉSENTATION STREAMLIT (1 minute)**

**Speaker Script:**
```
"Voici notre interface utilisateur Streamlit. C'est une interface intuitive
pour les professionnels de santé pour poser des questions médicales.

Vous pouvez voir ici la zone de saisie où l'on peut entrer une query 
médicale en langage naturel."
```

**Actions:**
1. Montrer l'interface Streamlit
2. Pointer vers la zone de saisie de query
3. Expliquer que l'interface est conçue pour être simple à utiliser

**Speaker Script (suite):**
```
"Pour la démonstration, je vais poser une query sur les symptômes du 
diabète de type 2, une question médicale très courante."
```

**Actions:**
1. Taper la query: "Quels sont les symptômes du diabète de type 2 ?"
2. Cliquer sur le bouton "Query" ou "Process"
3. Attendre le traitement (environ 1-2 secondes)

---

### **1:30 - PIPELINE RAG (30 secondes)**

**Speaker Script:**
```
"L'application a maintenant traité la query. Le pipeline RAG a effectué 
plusieurs étapes:

1. D'abord, elle a transformé la question en embedding vectoriel avec 
   notre modèle MiniLM-L6-v2.

2. Ensuite, elle a effectué un retrieval vectoriel dans notre base 
   ChromaDB pour trouver les chunks les plus pertinents.

3. Enfin, elle a affiché les chunks avec leurs scores de similarité et 
   généré une réponse contextuelle."
```

**Actions:**
1. Pointer vers les résultats affichés
2. Montrer les 5 chunks les plus pertinents
3. Pointer vers les scores de similarité (ex: 0.85, 0.78, 0.72...)
4. Montrer que chaque chunk a une source et un score

**Speaker Script (suite):**
```
"Vous pouvez voir ici que le système a retrouvé 5 chunks pertinents sur 
le diabète avec des scores de similarité élevés. Le chunk le plus pertinent
a un score de 0.85, ce qui indique une forte correspondance sémantique."
```

---

### **2:00 - MLFLOW TRACKING (30 secondes)**

**Speaker Script:**
```
"Maintenant je vais vous montrer le tracking de nos expériences dans MLflow. 
C'est crucial pour assurer la traçabilité et la reproductibilité de nos modèles."
```

**Actions:**
1. Ouvrir un nouvel onglet navigateur sur http://localhost:5000
2. Montrer l'interface MLflow UI
3. Cliquer sur l'expérience "medical_rag_experiments"

**Speaker Script (suite):**
```
"Vous pouvez voir ici nos différentes expériences d'entraînement. Nous avons
comparé plusieurs modèles d'embeddings et stratégies de chunking.

Chaque run enregistre les hyperparamètres, les métriques de performance,
et les artefacts pour assurer la reproductibilité."
```

**Actions:**
1. Cliquer sur un run spécifique (ex: "embedding_minilm")
2. Montrer les params (embedding_dim=384, chunk_size=1000)
3. Montrer les metrics (MRR=1.0, retrieval_time=50ms)
4. Montrer que le système assure une traçabilité complète

---

### **2:30 - MÉTRIQUES RAG (20 secondes)**

**Speaker Script:**
```
"Enfin, je vais vous montrer nos métriques de performance du système RAG."
```

**Actions:**
1. Retourner sur l'interface Streamlit
2. Pointer vers les métriques affichées (si disponibles)
3. Ou ouvrir l'endpoint API http://localhost:8000/metrics

**Speaker Script (suite):**
```
"Nos métriques montrent que:
- Le retrieval prend moins de 50ms par query
- Le MRR (Mean Reciprocal Rank) est parfait à 1.000 dans nos tests
- Le système peut traiter des centaines de queries par seconde
- Les embeddings sont performants pour le domaine médical"
```

---

### **2:50 - CONCLUSION (10 secondes)**

**Speaker Script:**
```
"Cette démonstration montre que notre prototype RAG fonctionne correctement
et peut être étendu avec des modèles médicaux spécialisés comme BioBERT.

Le système est maintenant prêt pour être déployé en production avec un 
monitoring complet via Prometheus et Grafana."

"Je suis maintenant disponible pour répondre à vos questions."
```

---

## 🎤 TIPS DÉMO LIVE

### **Pendant la Démo:**
- [ ] Parler lentement et clairement
- [ ] Pointer vers les éléments importants à l'écran
- [ ] Expliquer ce qui se passe "behind the scenes"
- [ ] Être prêt à gérer les problèmes techniques
- [ ] Avoir un plan de backup si Streamlit ne fonctionne pas

### **Plan Backup:**
```bash
# Si Streamlit échoue:
1. Utiliser l'API directement avec curl
2. Montrer les résultats en JSON
3. Expliquer que l'interface est en maintenance
4. Continuer avec MLflow et metrics

# Commande API backup:
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"text":"diabetes symptoms","top_k":5}'
```

### **Questions Difficiles:**

**Q: "Pourquoi RAG et pas un LLM direct ?"**
```
A: "RAG garantit des réponses sourcées et traçables, crucial dans le 
domaine médical. Les LLMs peuvent halluciner, mais RAG utilise des 
documents réels comme base."
```

**Q: "Comment ça se passe avec des millions de documents ?"**
```
A: "Excellent question. La scalability est dans notre roadmap avec des 
optimisations vectorielles, indexing avancé, et déploiement cloud."
```

**Q: "Les réponses sont certifiées médicalement ?"**
```
A: "Pour l'instant c'est un prototype. La certification médicale demanderait
une validation clinique et des modèles spécialisés comme BioBERT."
```

---

## 📊 CHECKLIST DÉMO COMPLÈTE

### **Avant (30 min avant):**
- [ ] Lancer API FastAPI (port 8000)
- [ ] Lancer Streamlit (port 8501)
- [ ] Lancer MLflow UI (port 5000)
- [ ] Vérifier tous les endpoints (health, query, metrics)
- [ ] Préparer la query médicale de test
- [ ] Préparer screenshots de backup
- [ ] Tester le scénario complet 3 fois

### **Pendant:**
- [ ] Suivre le timing (3 min total)
- [ ] Parler clairement et avec enthousiasme
- [ ] Pointer vers les éléments importants
- [ ] Gérer les problèmes techniques calmement
- [ ] Être prêt pour questions Q&A

### **Après:**
- [ ] Arrêter les services proprement
- [ ] Documenter les feedbacks reçus
- [ ] Noter les améliorations suggérées
- [ ] Planifier les prochaines étapes

---

## 🎯 TIMING PRÉCIS

| Temps | Étape | Action |
|-------|------|--------|
| 0:00-0:30 | Introduction | Montrer services, ouvrir Streamlit |
| 0:30-1:30 | Streamlit Demo | Saisir query, cliquer, montrer résultats |
| 1:30-2:00 | Pipeline RAG | Expliquer étapes, montrer chunks |
| 2:00-2:30 | MLflow Tracking | Ouvrir MLflow, montrer runs |
| 2:30-2:50 | Métriques RAG | Afficher performance metrics |
| 2:50-3:00 | Conclusion | Résumer, ouvrir Q&A |

---

**Bonne démo ! 🎬🚀**