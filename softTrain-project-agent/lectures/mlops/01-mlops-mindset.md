# MLOps mindset

## Abstract

MLOps is not "DevOps for machine learning." It's a set of practices that emerge once you stop thinking of a model as the *artifact you ship* and start thinking of it as one component of a *system you operate*. The mindset shift — from model-as-artifact to system-as-product — drives every other MLOps practice.

## Motivation

A common pattern in young ML teams: a data scientist trains a model, hands a `.pkl` file (or a notebook) to engineering, and walks away. Six weeks later the model is in production, scoring requests. Three months later it starts producing wrong predictions and nobody can figure out why. There's no record of what data it trained on, no monitoring of input distributions, no path to retrain, no rollback story. The team realises that the *model* was 5% of the work; the other 95% — versioning, evaluation, monitoring, deployment, retraining, observability — is the system.

Most ML teams discover this the hard way. The learning aim of this lecture is to give you the mindset *before* you discover it.

The motivating image is from Sculley et al's "Hidden Technical Debt in Machine Learning Systems" (Google, 2014). The famous diagram shows a tiny "ML code" box in the middle, surrounded by enormous boxes for configuration, data collection, feature extraction, monitoring, serving infrastructure, etc. The ML code is the smallest piece.

## Core concepts

### The mindset shift: model → system → product

Three frames, each containing the previous:

- **Model frame** — "I trained a model. It has 92% accuracy." Stops at the artifact.
- **System frame** — "I have a model that's served behind an HTTP endpoint, retrained nightly, monitored for drift." Treats the model as one component.
- **Product frame** — "We have a recommendation system whose ultimate measure is users-who-clicked. The model is one lever; the UI, the cold-start rules, the post-filter, and the A/B framework are equally important."

ML-naive teams operate at the model frame. ML-mature teams operate at the system or product frame. The vocabulary you use ("the model is in production" vs "the system is shipping recommendations") leaks the frame.

### The four core practices

Every MLOps maturity model points at the same four areas. Names vary; substance is the same.

#### 1. Reproducibility

If you can't re-run training and get the same model out, you don't have a model — you have an artifact you can't trust. Reproducibility means versioning *the data*, *the code*, and *the environment* together. A trained model is the deterministic output of `(data, code, hyperparameters, environment)`; if any of those four can change without recording it, your model is irreproducible.

In practice:
- Data versioning (DVC, LakeFS, or copying snapshots into an immutable bucket).
- Code versioning (git — but training scripts often live outside the main repo, which is a smell).
- Environment versioning (Docker, conda envs with pinned dependencies, or `requirements.lock.txt`).
- Hyperparameters tracked alongside the model.

#### 2. Experiment tracking

ML development is essentially an empirical science: try things, measure, keep what works. Without tracking, you cannot answer "did changing the loss function help, or did the seed change?" — and you will be unable to defend modelling choices six months later.

Tools (MLflow, Weights & Biases, Neptune, or a humble Postgres table) all do the same job: record `(experiment_id, code commit, data version, hyperparameters, metrics)` for every training run.

The cheap-and-cheerful version is a CSV. The expensive version is a hosted dashboard. Both are infinitely better than no tracking.

#### 3. Deployment patterns

How models reach predictions in the wild. Four broad patterns:

- **Batch** — score every record overnight; serve from a precomputed table. Cheapest. Works when freshness > 1 hour is OK.
- **Online** (request/response) — score on demand from an HTTP endpoint. Standard for recommendation, fraud detection, search ranking. Latency-sensitive.
- **Streaming** — events flow in continuously; the model scores each as it arrives. Used for real-time fraud, anomaly detection.
- **Embedded** — the model runs inside the consuming application (mobile app, browser, edge device). Privacy-preserving but harder to update.

The choice has cascading consequences for monitoring, retraining cadence, and acceptable latency. Treat it as an architectural decision, not a deployment detail.

#### 4. Monitoring and drift

The four things to monitor:

- **Operational health** — latency, error rate, throughput. Same as any service.
- **Input data drift** — is the distribution of inputs your model sees today different from training? (Covariate shift.)
- **Prediction drift** — is the distribution of *outputs* the model emits changing? Sometimes precedes input drift becoming detectable.
- **Performance / outcome metrics** — when ground truth becomes available (a click, a chargeback), does the model's predicted-vs-actual rate hold up? (Concept drift.)

Operational monitoring is well-understood (Prometheus, Datadog). Drift monitoring is less standardised; libraries like Evidently and WhyLabs help, but the *judgement* of "is this drift serious" remains a human call.

### The hidden practice: versioning the *contract*

Less-discussed but essential: the *interface* between the model and its consumers (input features, output schema, expected error modes) is a contract. When the model is retrained with a new feature, the contract changes. Failing to version the contract — or to communicate the change — produces silent bugs.

Mature teams treat the model's serialised input and output as a Pydantic / Zod schema, version it, and reject mismatched requests at the boundary.

### Training/serving skew

The single most common ML production bug: features computed differently in training (offline, in pandas) versus serving (online, in production code). The model has been trained on slightly different inputs than it sees in prod.

Causes are mundane: timezones, default-value handling, capitalisation, missing-value imputation, ordering of one-hot encoding. The fix is either:

- A **feature store** that computes features once and serves them to both training and inference. Modern but expensive.
- **Shared feature-computation code** between offline and online — the same module computes features whether called from a training notebook or a serving endpoint.

The cheap fix (shared code) catches 95% of the cases. Don't build a feature store before you've made the cheap fix work.

## Tradeoffs / counterpoints

### MLOps tooling can outweigh model value

It's possible to spend more engineering time on the MLOps platform than on the actual model — and produce a system that delivers the same value as a SQL query on a precomputed table. Before building infrastructure, ask: *what is the marginal value of the model over the simplest possible heuristic?* If the answer is unclear, you don't need MLOps; you need a baseline.

### "Production-grade" can mean nothing

The phrase "production-grade ML pipeline" gets used loosely. It can mean anything from "a Python script in cron" to "a Kubeflow pipeline with feature store, model registry, online serving, drift detection, and human-in-the-loop retraining." Be specific. The level of MLOps investment should match the *cost of the model being wrong*, not the team's appetite for tooling.

### Retraining cadence as a product decision

How often to retrain isn't a technical choice — it's a product decision about how much non-stationarity you can tolerate vs. how much retraining costs. A fraud model in a fast-moving market may need daily retraining; a credit-scoring model in a regulated context may retrain quarterly with formal review.

A common failure: teams set up nightly retraining on autopilot, then can't say *why* nightly. When regulators or auditors ask, they have no answer. Decide the cadence deliberately.

### When NOT to retrain

If the cause of drift is a *bug* (a renamed source column, a broken upstream feed), retraining will lock the bug in. Investigate before retraining. Most teams discover this the hard way: drift alarm fires → automatic retrain → model now happily consumes corrupt data → predictions are quietly wrong for weeks.

### The org-shape problem

MLOps is, in many companies, the political problem of *who owns the system once a model is in it*. Data scientists want to focus on modelling. SRE teams want to operate well-defined services. The model-shaped object falls in the gap. Mature orgs adopt one of two patterns:

- **Embedded ML engineers** — engineers with ML literacy live inside the data science team and own the path to production.
- **ML platform team** — central team builds reusable infrastructure (training, serving, monitoring) so DS teams can self-serve.

Both work. Hybrid usually doesn't, because nobody owns the whole system.

## Further reading

1. **Sculley et al, *Hidden Technical Debt in Machine Learning Systems* (NeurIPS 2014)** — the foundational paper. Read it twice.
2. **Chip Huyen, *Designing Machine Learning Systems* (2022)** — book-length, practical, opinionated. The best modern overview.
3. **Martin Fowler / Thoughtworks — *Continuous Delivery for Machine Learning* (CD4ML)** ([martinfowler.com/articles/cd4ml.html](https://martinfowler.com/articles/cd4ml.html)) — the article that named the discipline.
4. **Google — *Rules of Machine Learning: Best Practices for ML Engineering*** ([developers.google.com/machine-learning/guides/rules-of-ml](https://developers.google.com/machine-learning/guides/rules-of-ml)) — 43 rules from real Google production. Many are surprisingly product-shaped.
5. **MadeWithML.com — Goku Mohandas's MLOps course** — code-heavy walkthrough of building a small MLOps stack end-to-end.

## Discussion prompts

1. **Pick a model you've trained (in a course, a project, anywhere).** Could you reproduce its training today, exactly? Walk through what you'd need to gather, what's missing, and what you'd change next time.
2. **Describe a specific failure mode of "training/serving skew."** When have you seen, or could you imagine, a case where a feature was computed slightly differently online vs. offline, and what was the consequence? How would you have caught it before production?
3. **Argue against MLOps for a small team.** Sketch a scenario in which a 3-person team should *not* build experiment tracking, drift monitoring, and a feature store — what's the minimum they should do instead, and where does that minimum break?
4. **The phrase "the model is in production" carries a frame.** Rewrite a few engineering conversations from a "system in production" frame instead. Does the language change what you'd build? What you'd monitor?
5. **Sculley's diagram shows the ML code as a tiny box.** Pick another technology (a database, a frontend framework, a build tool) and try to draw the equivalent diagram for it. Is the ratio of "core code" to "everything else" similar? Why or why not?
