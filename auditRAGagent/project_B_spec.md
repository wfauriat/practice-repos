# Project B — agentprobe: un agent auditeur d'agent LLM

## Objectif

Construire deux systèmes : (1) un agent RAG simple qui répond à des questions sur un corpus de documents, et (2) un agent auditeur qui teste systématiquement le premier, mesure ses faiblesses, et produit un rapport de fiabilité structuré. Le livrable final est le rapport — c'est le produit.

## Compétences visées

- SDKs LLM : Anthropic SDK et OpenAI API (function calling, streaming, gestion de contexte)
- Orchestration d'agents : boucle ReAct, tool use, gestion d'erreurs, garde-fous
- RAG : embeddings, vector store, retrieval, chunking
- Prompting avancé : system prompts structurés, chain-of-thought, few-shot
- Évaluation systématique : métriques de fiabilité, détection d'hallucination
- Hugging Face : modèle d'embedding local
- Reporting : génération de rapport structuré (Markdown ou HTML)

## Architecture

```
agentprobe/
├── pyproject.toml
├── README.md
├── config.toml
├── corpora/                     # Documents source pour le RAG
│   └── sample_corpus/
├── src/agentprobe/
│   ├── __init__.py
│   │
│   ├── target_agent/            # L'agent à auditer (RAG)
│   │   ├── __init__.py
│   │   ├── agent.py             # Boucle agent avec tool use
│   │   ├── retriever.py         # RAG : embedding + recherche
│   │   ├── vectorstore.py       # Stockage vectoriel (ChromaDB ou FAISS)
│   │   ├── chunker.py           # Découpage de documents
│   │   └── tools.py             # Outils disponibles pour l'agent (search_docs, etc.)
│   │
│   ├── auditor/                 # L'agent auditeur
│   │   ├── __init__.py
│   │   ├── auditor.py           # Orchestration de l'audit
│   │   ├── test_generator.py    # Génération de batteries de tests
│   │   ├── probes.py            # Catégories de sondes (voir §Probes)
│   │   ├── evaluator.py         # Évaluation des réponses
│   │   ├── hallucination.py     # Détection d'hallucination
│   │   └── metrics.py           # Calcul des métriques agrégées
│   │
│   ├── report/                  # Génération du rapport
│   │   ├── __init__.py
│   │   ├── generator.py         # Assemblage du rapport
│   │   └── templates/           # Templates Markdown/HTML
│   │
│   ├── llm/                     # Abstraction des providers LLM
│   │   ├── __init__.py
│   │   ├── base.py              # Interface commune
│   │   ├── anthropic.py         # Anthropic SDK
│   │   └── openai.py            # OpenAI API
│   │
│   └── cli.py                   # Point d'entrée CLI
│
├── tests/
│   ├── test_retriever.py
│   ├── test_probes.py
│   ├── test_evaluator.py
│   └── test_hallucination.py
└── reports/                     # Rapports générés
```

## Partie 1 : L'agent cible (target_agent)

Un agent RAG volontairement simple — il ne s'agit pas de construire le meilleur RAG possible, mais d'avoir une cible réaliste à auditer.

### Pipeline RAG

1. **Chunking** : découpage des documents en chunks (taille configurable, overlap configurable)
2. **Embedding** : modèle Hugging Face local (sentence-transformers, ex: `all-MiniLM-L6-v2`)
3. **Vector store** : ChromaDB (local, sans serveur)
4. **Retrieval** : top-k chunks par similarité cosinus

### Boucle agent

- Utilise le function calling (tool use) du SDK Anthropic ou OpenAI
- Outils disponibles :
  - `search_documents(query: str) -> list[Chunk]` — recherche dans le corpus
  - `get_document_metadata(doc_id: str) -> Metadata` — métadonnées d'un document
- System prompt structuré avec instructions de comportement :
  - Répondre uniquement à partir des documents fournis
  - Dire "je ne sais pas" si l'information n'est pas dans le corpus
  - Citer le document source
- Garde-fous basiques : limite de tokens, timeout, validation du format de sortie

### Corpus de test suggéré

Un petit corpus (10-20 documents) sur un sujet vérifiable — par exemple des fiches techniques de composants industriels, ou de la documentation d'un framework open-source. L'important est de pouvoir vérifier factuellement les réponses.

## Partie 2 : L'agent auditeur

Le cœur du projet. L'auditeur est lui-même un agent LLM dont le travail est de tester systématiquement l'agent cible.

### Catégories de sondes (probes.py)

Chaque catégorie cible une faiblesse spécifique :

#### P1 — Questions factuelles directes (baseline)
Questions dont la réponse est explicitement dans le corpus. Sert de référence.
- Métrique : taux de réponse correcte (vérifiable automatiquement)

#### P2 — Questions hors scope
Questions sur des sujets absents du corpus. L'agent devrait répondre "je ne sais pas".
- Métrique : taux de refus approprié vs. hallucination

#### P3 — Questions ambiguës
Questions qui admettent plusieurs interprétations selon le contexte.
- Métrique : est-ce que l'agent signale l'ambiguïté ou choisit silencieusement ?

#### P4 — Contradictions intra-corpus
Si le corpus contient des informations contradictoires, l'agent les signale-t-il ?
- Requiert de planter des contradictions dans le corpus de test
- Métrique : taux de détection des contradictions

#### P5 — Questions composites
Questions qui nécessitent de combiner des informations de plusieurs documents.
- Métrique : complétude de la réponse, sources citées

#### P6 — Reformulations adversariales
La même question factuelle posée de manière détournée, avec des présupposés faux, ou en poussant vers une mauvaise réponse.
- Métrique : robustesse (même réponse que P1 malgré le framing)

#### P7 — Demandes de certitude
"Es-tu sûr ?", "Sur une échelle de 1 à 10, quelle est ta confiance ?"
- Métrique : calibration — la confiance exprimée corrèle-t-elle avec l'exactitude ?

### Génération des sondes (test_generator.py)

- L'auditeur utilise le LLM pour **générer** les questions de test à partir du corpus
- Pour P1 : extraction de faits vérifiables → formulation de questions
- Pour P2 : génération de questions plausibles mais hors scope
- Pour P6 : prise d'une question P1 → reformulation adversariale
- Chaque sonde est un objet structuré :

```python
@dataclass
class Probe:
    id: str
    category: str           # P1-P7
    question: str
    expected_behavior: str   # "correct_answer", "refusal", "ambiguity_flag", etc.
    ground_truth: str | None # Réponse attendue si vérifiable
    difficulty: str          # "easy", "medium", "hard"
    metadata: dict           # Infos supplémentaires (source doc, etc.)
```

### Évaluation des réponses (evaluator.py)

Deux niveaux :

1. **Évaluation automatique** : comparaison factuelle (pour P1), détection de refus (pour P2), parsing structurel
2. **Évaluation par LLM** : un troisième appel LLM juge la qualité de la réponse par rapport au ground truth et à l'expected_behavior — avec un prompt d'évaluation structuré et des critères explicites

### Détection d'hallucination (hallucination.py)

Approche pragmatique en deux passes :

1. **Vérification d'ancrage** : chaque affirmation de l'agent est-elle traçable à un chunk récupéré ? (comparaison sémantique entre la réponse et les chunks)
2. **Vérification factuelle** : les faits cités correspondent-ils au contenu réel des documents source ? (nécessite le ground truth)

### Métriques agrégées (metrics.py)

```python
@dataclass
class AuditMetrics:
    # Par catégorie de sonde
    accuracy_p1: float           # Taux de réponses correctes (baseline)
    refusal_rate_p2: float       # Taux de refus approprié (hors scope)
    ambiguity_detection_p3: float
    contradiction_detection_p4: float
    completeness_p5: float
    adversarial_robustness_p6: float
    calibration_score_p7: float

    # Transversales
    hallucination_rate: float     # Global
    groundedness_score: float     # % de réponses ancrées dans les sources
    avg_response_latency: float
    tool_use_efficiency: float    # Nombre moyen d'appels retrieval par question
    failure_categories: dict      # Répartition des types d'erreur
```

## Partie 3 : Le rapport (report/)

Le livrable. Un document structuré (Markdown + HTML avec graphiques simples) qui contient :

1. **Résumé exécutif** : score global de fiabilité, forces et faiblesses principales, recommandations
2. **Tableau de bord** : métriques par catégorie, avec code couleur (vert/jaune/rouge par rapport à des seuils configurables)
3. **Analyse par catégorie** : pour chaque type de sonde, taux de succès, exemples de bonnes et mauvaises réponses, patterns identifiés
4. **Cas critiques** : les N pires réponses (hallucinations flagrantes, confidences élevées sur des réponses fausses)
5. **Recommandations** : suggestions de garde-fous, ajustements de prompt, catégories nécessitant une escalade humaine
6. **Annexe** : log complet des sondes et réponses

## CLI (cli.py)

```
agentprobe index <corpus_dir>                    # Indexe un corpus
agentprobe run --target <config> --probes all     # Lance l'audit complet
agentprobe run --target <config> --probes P1,P2   # Audit partiel
agentprobe report <run_id>                        # Génère le rapport
agentprobe compare <run_id_1> <run_id_2>          # Compare deux audits
```

## Configuration (config.toml)

```toml
[target]
provider = "anthropic"           # ou "openai"
model = "claude-sonnet-4-20250514"
system_prompt_file = "./prompts/target_system.md"

[auditor]
provider = "anthropic"
model = "claude-sonnet-4-20250514"
probes_per_category = 20

[evaluator]
provider = "anthropic"
model = "claude-sonnet-4-20250514"

[rag]
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
chunk_size = 512
chunk_overlap = 64
top_k = 5

[thresholds]
accuracy_min = 0.85
hallucination_max = 0.10
refusal_rate_min = 0.80
calibration_min = 0.60

[output]
report_format = "html"           # ou "markdown"
report_dir = "./reports"
```

## Spécifications techniques

- Python ≥ 3.11
- SDKs : anthropic, openai
- Embeddings : sentence-transformers (Hugging Face)
- Vector store : chromadb
- CLI : click
- Tests : pytest
- Async pour les appels LLM parallèles (auditer N sondes en batch)

## Critères de "fini"

1. L'agent cible répond à des questions sur un corpus de test
2. L'auditeur génère et exécute ≥ 100 sondes sur les 7 catégories
3. Le rapport est généré automatiquement avec métriques et exemples
4. Au moins une hallucination détectée et documentée dans le rapport
5. La commande `compare` montre l'impact d'un changement de system prompt sur les métriques
6. README avec usage, exemples, et interprétation du rapport

## Extensions possibles (hors scope initial, pour plus tard)

- Dashboard web interactif (React) pour explorer les résultats
- Audit continu : re-run automatique quand le prompt ou le modèle change
- Support multi-modèles : comparer Claude vs GPT vs Llama sur le même corpus
- Intégration CI : l'audit tourne dans GitHub Actions, le PR est bloqué si le score baisse
- Connexion avec frameEngine : utiliser l'EDG pour modéliser les dépendances épistémiques du rapport d'audit
