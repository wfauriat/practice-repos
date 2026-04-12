# agentprobe

Systematically audit LLM RAG agents. agentprobe generates test probes across 7 categories, runs them against a target agent, evaluates responses, detects hallucinations, and produces a structured reliability report.

## Architecture

```
Target Agent (RAG)          Auditor Agent              Report
┌──────────────────┐   ┌─────────────────────┐   ┌──────────────┐
│ Corpus → Chunks  │   │ Probe Generator     │   │ HTML / MD    │
│ Embeddings       │◄──│ 7 categories (P1-P7)│──►│ Dashboard    │
│ ChromaDB         │   │ Evaluator (auto+LLM)│   │ Metrics      │
│ Agent Loop       │   │ Hallucination Check  │   │ Recommendations│
│ Tool Use         │   │ Metrics Aggregation  │   │ Probe Log    │
└──────────────────┘   └─────────────────────┘   └──────────────┘
```

## Install

```bash
# Clone and set up
git clone <repo-url> && cd agentprobe
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Configure API key
echo 'ANTHROPIC_API_KEY="sk-ant-..."' > .env
source .env && export ANTHROPIC_API_KEY
```

Requires Python 3.11+.

## Quick Start

```bash
# 1. Index the sample corpus (15 technical documents, ~156 chunks)
agentprobe index corpora/sample_corpus

# 2. Test the target agent manually
agentprobe ask "What is the temperature range of the MI-T100?"

# 3. Run a full audit (generates ~140 probes across all 7 categories)
agentprobe run --probes all

# 4. Generate the HTML report
agentprobe report <run_id>

# 5. Change the system prompt, re-run, and compare
agentprobe run --probes all
agentprobe compare <run_id_1> <run_id_2>
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `agentprobe index <corpus_dir>` | Chunk and embed documents into ChromaDB |
| `agentprobe ask "<question>"` | Ask the target agent a question |
| `agentprobe info` | Show indexed corpus stats |
| `agentprobe run --probes all` | Run a full audit |
| `agentprobe run --probes P1,P2` | Run specific probe categories |
| `agentprobe run --no-llm-judge` | Skip LLM-as-judge evaluation (faster) |
| `agentprobe report <run_id>` | Generate HTML/Markdown report from a saved run |
| `agentprobe report <run_id> --format markdown` | Generate Markdown report |
| `agentprobe compare <run_a> <run_b>` | Show metric deltas between two runs |

All commands accept `--config/-c <path>` to specify a config file (default: `config.toml`).

## Probe Categories

| Category | Tests | Expected Agent Behavior |
|----------|-------|------------------------|
| **P1** Factual | Direct questions from corpus | Correct, sourced answer |
| **P2** Out-of-scope | Questions not in corpus | Refusal ("I don't know") |
| **P3** Ambiguous | Multiple valid interpretations | Flag the ambiguity |
| **P4** Contradiction | Conflicting info across docs | Detect and report conflict |
| **P5** Composite | Requires multiple documents | Complete, multi-source answer |
| **P6** Adversarial | Misleading framing / false presuppositions | Same correct answer as P1 |
| **P7** Certainty | "Are you sure?" / confidence probes | Calibrated confidence |

## Report

The generated report includes:

1. **Executive summary** — composite reliability score, key stats
2. **Metrics dashboard** — color-coded per-category scores (green/orange/red)
3. **Per-category analysis** — pass rates with good and bad examples
4. **Critical cases** — worst failures, hallucinations flagged
5. **Recommendations** — actionable suggestions based on threshold violations
6. **Appendix** — full probe log with scores

## Configuration

Edit `config.toml`:

```toml
[target]
provider = "anthropic"           # or "openai"
model = "claude-sonnet-4-20250514"
system_prompt_file = "./prompts/target_system.md"

[auditor]
provider = "anthropic"
model = "claude-sonnet-4-20250514"
probes_per_category = 20         # 20 × 7 = 140 probes total

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
report_format = "html"           # or "markdown"
report_dir = "./reports"
```

## Custom Corpus

Replace `corpora/sample_corpus/` with your own Markdown or text files, then re-index:

```bash
agentprobe index path/to/your/docs
```

The corpus should contain factually verifiable content. For best audit coverage, include 10+ documents with overlapping topics.

## Tests

```bash
pytest tests/ -v
```

93 tests covering the chunker, vector store, retriever, agent tools, evaluator, hallucination checker, metrics aggregation, and report generation — all runnable without API keys.

## Project Structure

```
src/agentprobe/
├── cli.py                    # Click CLI (index, ask, run, report, compare)
├── llm/                      # LLM provider abstraction
│   ├── base.py               # LLMProvider ABC, ToolCall, LLMResponse
│   ├── anthropic.py          # Anthropic Messages API
│   └── openai.py             # OpenAI Chat Completions API
├── target_agent/             # The RAG agent under test
│   ├── chunker.py            # Paragraph-aware document chunking
│   ├── vectorstore.py        # ChromaDB + sentence-transformers
│   ├── retriever.py          # Orchestrates chunking + search
│   ├── tools.py              # search_documents, get_document_metadata
│   └── agent.py              # ReAct agent loop with tool use
├── auditor/                  # The auditor agent
│   ├── probes.py             # Probe dataclass, 7 categories
│   ├── test_generator.py     # LLM-powered probe generation
│   ├── evaluator.py          # Automatic + LLM-as-judge evaluation
│   ├── hallucination.py      # Grounding + factual verification
│   ├── metrics.py            # Aggregate audit metrics
│   └── auditor.py            # Main orchestrator
└── report/                   # Report generation
    └── generator.py          # HTML + Markdown report builder
```
