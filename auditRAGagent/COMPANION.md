# agentprobe -- Companion Guide

A guided walkthrough of the agentprobe codebase, focused on LLM agent design, API integration, and evaluation patterns.

---

## How to Use This Guide

Open this document alongside the source code. Each Part points you to specific files and line ranges. Read the code first, then come back here for the "why" behind the design.

**Setup** (if you want to run experiments as you read):

```bash
cd /path/to/agentprobe
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
echo 'ANTHROPIC_API_KEY="sk-ant-..."' > .env
```

**Conventions used below:**

- `file.py:10-25` means lines 10 through 25 of that file.
- **Refresher** blocks explain an LLM/agent concept from scratch the first time it appears. They are indented and self-contained -- skip them if you already know the concept.
- **Try it** blocks suggest small terminal experiments.
- **Design note** blocks explain why the code is written this way.

---

## Reading Order

The modules are ordered so you never encounter an import you have not already studied.

| # | File | Role |
|---|------|------|
| 1 | `pyproject.toml` | Project metadata, dependencies, CLI entry point |
| 2 | `config.toml` | Runtime configuration for all three subsystems |
| 3 | `src/agentprobe/llm/base.py` | Provider-agnostic LLM interface |
| 4 | `src/agentprobe/llm/anthropic.py` | Anthropic Messages API integration |
| 5 | `src/agentprobe/llm/openai.py` | OpenAI Chat Completions API integration |
| 6 | `src/agentprobe/target_agent/chunker.py` | Document splitting for RAG |
| 7 | `src/agentprobe/target_agent/vectorstore.py` | Embedding storage and similarity search |
| 8 | `src/agentprobe/target_agent/retriever.py` | Orchestrates chunking + vector search |
| 9 | `src/agentprobe/target_agent/tools.py` | Tool definitions the agent can call |
| 10 | `src/agentprobe/target_agent/agent.py` | The ReAct agent loop |
| 11 | `prompts/target_system.md` | System prompt as a behavioral contract |
| 12 | `src/agentprobe/auditor/probes.py` | Probe taxonomy (7 categories) |
| 13 | `src/agentprobe/auditor/test_generator.py` | LLM-powered probe generation |
| 14 | `src/agentprobe/auditor/evaluator.py` | Automatic + LLM-as-judge evaluation |
| 15 | `src/agentprobe/auditor/hallucination.py` | Grounding and factual verification |
| 16 | `src/agentprobe/auditor/metrics.py` | Aggregate audit metrics |
| 17 | `src/agentprobe/auditor/auditor.py` | Audit orchestrator |
| 18 | `src/agentprobe/report/generator.py` | HTML and Markdown report builder |
| 19 | `src/agentprobe/cli.py` | CLI entry point tying everything together |
| 20 | `tests/` | Test suite |

---

## Part 1 -- Project Configuration

**Read:** `pyproject.toml` (full file), `config.toml` (full file)

### pyproject.toml -- What the project needs

The dependency list (`pyproject.toml:10-17`) tells you the technology stack:

```toml
dependencies = [
    "anthropic>=0.39.0",     # Anthropic Claude SDK
    "openai>=1.50.0",        # OpenAI SDK
    "sentence-transformers>=3.0.0",  # Local embedding models
    "chromadb>=0.5.0",       # Vector database
    "click>=8.1.0",          # CLI framework
    "python-dotenv>=1.0.0",  # Load API keys from .env
]
```

The CLI entry point is registered at line 26: `agentprobe = "agentprobe.cli:main"`. This means running `agentprobe` in the terminal calls the `main()` function in `cli.py`.

### config.toml -- Three subsystems, one config

The config file separates concerns into sections that map directly to the architecture:

- `[target]` -- which LLM powers the agent being tested
- `[auditor]` -- which LLM generates test probes
- `[evaluator]` -- which LLM acts as judge (can be a different model)
- `[rag]` -- embedding model, chunk sizes, retrieval depth
- `[thresholds]` -- pass/fail boundaries for the audit report
- `[output]` -- report format and directory

> **Design note.** Using three separate LLM configurations (`target`, `auditor`, `evaluator`) means you can test a cheap model as target while using a strong model as judge, or compare providers by changing one line. This separation is a common pattern in LLM evaluation frameworks.

---

## Part 2 -- LLM Provider Abstraction

**Read:** `src/agentprobe/llm/base.py` (full file)

### The problem: two APIs, one codebase

Anthropic and OpenAI both offer chat + tool-use APIs, but their message formats, tool-call schemas, and response structures differ significantly. This module defines a single interface so the rest of the codebase never thinks about which provider it is talking to.

> **Refresher: Provider abstraction pattern**
>
> When you need to support multiple LLM backends (Anthropic, OpenAI, local models), you define an abstract interface that captures the common capabilities: "send messages, get a response that may contain text and/or tool calls." Each concrete provider translates between this common interface and its native API format.
>
> This is sometimes called the **Adapter pattern** -- the provider classes adapt each vendor's API to a uniform internal protocol.

### The data model (`base.py:9-33`)

Three frozen dataclasses capture everything that flows between the application and any LLM:

```python
@dataclass(frozen=True)
class ToolCall:
    id: str          # Unique ID assigned by the API (used to match results back)
    name: str        # Which tool the LLM wants to call
    arguments: dict  # The arguments it wants to pass

@dataclass(frozen=True)
class TokenUsage:
    input_tokens: int = 0
    output_tokens: int = 0

@dataclass(frozen=True)
class LLMResponse:
    content: str | None = None          # Text portion of the response
    tool_calls: list[ToolCall] = ...    # Zero or more tool invocations
    usage: TokenUsage = ...
    stop_reason: str = "end_turn"       # Why the model stopped generating
```

> **Refresher: Tool calls in LLM APIs**
>
> Modern LLMs do not just generate text. When you provide **tool definitions** (describing functions the model can invoke), the model may respond with a structured request to call one of those tools instead of (or in addition to) producing text.
>
> The flow is:
> 1. You send a message + tool definitions to the API
> 2. The model returns either text, or a `tool_call` (name + arguments)
> 3. You execute the tool locally and send the result back
> 4. The model uses the result to formulate its final answer
>
> This is the foundation of agent behavior -- the LLM decides *when* to use tools and *what arguments* to pass. The `ToolCall` dataclass above captures one such request.

### The abstract interface (`base.py:36-61`)

```python
class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages, *, system=None, tools=None, temperature=0.0) -> LLMResponse:
```

Key design decisions:
- **`messages`** is `list[dict]` -- the raw message format for the provider. This avoids a second abstraction layer over message construction.
- **`system`** is separate from messages because Anthropic treats it as a top-level parameter while OpenAI inserts it as the first message. Each provider handles this differently.
- **`tools`** are provider-specific dicts. Tool definitions differ between Anthropic and OpenAI (see next two files).
- **`async`** because LLM API calls take seconds. Without async, running 35 probes sequentially at ~10 seconds each would take 6 minutes. With async + concurrency, you can overlap multiple calls.

---

## Part 3 -- Anthropic Provider

**Read:** `src/agentprobe/llm/anthropic.py` (full file)

> **Refresher: The Anthropic Messages API**
>
> Anthropic's API uses a `messages.create()` call with this structure:
> ```python
> response = client.messages.create(
>     model="claude-sonnet-4-20250514",
>     max_tokens=4096,
>     system="You are a helpful assistant.",   # Top-level, not in messages
>     messages=[{"role": "user", "content": "Hello"}],
>     tools=[...],          # Tool definitions with input_schema
>     temperature=0.0,
> )
> ```
>
> The response contains a list of **content blocks** -- each block is either `type: "text"` (a text response) or `type: "tool_use"` (a request to call a tool). A single response can contain both text AND tool calls.
>
> Tool results are sent back as a `user` message with `type: "tool_result"` content blocks, where each result is matched to its tool call by `tool_use_id`.

### Normalization (`anthropic.py:44-68`)

The `_normalise` method translates Anthropic's native response into the generic `LLMResponse`:

```python
for block in resp.content:
    if block.type == "text":
        content_text = block.text
    elif block.type == "tool_use":
        tool_calls.append(ToolCall(
            id=block.id,
            name=block.name,
            arguments=block.input if isinstance(block.input, dict) else json.loads(block.input),
        ))
```

The `arguments` handling (`isinstance` check on line 56) is defensive: Anthropic usually returns `input` as a dict, but in some edge cases it may be a JSON string.

### Rate limiting (`anthropic.py:16`)

```python
self._client = AsyncAnthropic(max_retries=5)
```

The Anthropic SDK has built-in retry with exponential backoff for 429 (rate limit) and 5xx errors. Setting `max_retries=5` makes the client resilient to temporary rate limits without any custom retry logic.

> **Refresher: LLM API rate limits**
>
> LLM APIs enforce limits on tokens-per-minute and requests-per-minute. When exceeded, the API returns HTTP 429. Your options:
> 1. **SDK-level retry** (what we do here) -- the SDK waits and retries automatically
> 2. **Application-level concurrency control** -- limit how many parallel calls you make (see Part 17)
> 3. **Queue-based throttling** -- for production systems, a token bucket or leaky bucket algorithm
>
> For agentprobe, the combination of `max_retries=5` and a concurrency semaphore in the auditor is sufficient.

### Tool definition format (`anthropic.py:74-80`)

Anthropic expects tool definitions with `input_schema`:

```python
{"name": "search_documents", "description": "...", "input_schema": {"type": "object", ...}}
```

### Tool result format (`anthropic.py:83-94`)

Tool results go in a `user` message with `tool_result` content blocks:

```python
{"role": "user", "content": [{"type": "tool_result", "tool_use_id": "...", "content": "..."}]}
```

Multiple tool results are batched into a single `user` message. This is an Anthropic API requirement -- sending them as separate messages causes errors.

---

## Part 4 -- OpenAI Provider

**Read:** `src/agentprobe/llm/openai.py` (full file)

> **Refresher: OpenAI Chat Completions with tools**
>
> OpenAI's API differs from Anthropic in several ways:
>
> | Aspect | Anthropic | OpenAI |
> |--------|-----------|--------|
> | System prompt | Top-level `system` parameter | First message with `role: "system"` |
> | Tool definitions | `input_schema` key | Wrapped in `{"type": "function", "function": {..., "parameters": ...}}` |
> | Tool calls in response | Content blocks with `type: "tool_use"` | Separate `tool_calls` array on the message |
> | Tool results | `user` message with `tool_result` blocks | Separate messages with `role: "tool"` |
> | Stop reason | `stop_reason` field | `finish_reason` on the choice |

### System prompt injection (`openai.py:29-31`)

```python
if system:
    full_messages.append({"role": "system", "content": system})
full_messages.extend(messages)
```

OpenAI expects the system prompt as the first message in the conversation, not as a separate API parameter.

### Tool result messages (`openai.py:89-96`)

Unlike Anthropic's batched approach, OpenAI expects each tool result as its own message:

```python
{"role": "tool", "tool_call_id": "...", "content": "..."}
```

> **Design note.** The differences between these two files illustrate *why* the provider abstraction exists. The agent loop in `agent.py` handles both formats because the providers normalize everything to `LLMResponse` on the way in, and helper methods build the correct message format on the way out.

**Try it:**

```python
# Compare tool definition formats side by side
from agentprobe.llm.anthropic import AnthropicProvider
from agentprobe.llm.openai import OpenAIProvider

schema = {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
print("Anthropic:", AnthropicProvider.tool_definition("search", "Search docs", schema))
print("OpenAI:  ", OpenAIProvider.tool_definition("search", "Search docs", schema))
```

---

## Part 5 -- Document Chunking

**Read:** `src/agentprobe/target_agent/chunker.py` (full file)

> **Refresher: Why RAG needs chunking**
>
> LLM context windows are limited. You cannot feed an entire document corpus into a prompt. Instead, RAG (**Retrieval-Augmented Generation**) works in stages:
>
> 1. **Chunk** -- split documents into small pieces (~500 characters)
> 2. **Embed** -- convert each chunk into a numeric vector using an embedding model
> 3. **Store** -- save vectors in a database that supports similarity search
> 4. **Retrieve** -- given a user question, embed it, find the most similar chunks
> 5. **Generate** -- send the retrieved chunks + question to the LLM as context
>
> Chunking quality directly affects retrieval quality. Bad chunks = bad retrieval = bad answers.

### Chunking strategy (`chunker.py:95-131`)

The chunker uses a **greedy paragraph-merging** strategy:

1. Split text on blank lines (paragraph boundaries)
2. Merge adjacent paragraphs into chunks up to `chunk_size` characters
3. If a single paragraph exceeds `chunk_size`, split it on sentence boundaries
4. If a sentence still exceeds `chunk_size`, hard-split by character count
5. Maintain `chunk_overlap` characters between consecutive chunks

> **Refresher: Chunk overlap**
>
> When you split text into chunks, information at chunk boundaries gets severed. A fact might start at the end of chunk 3 and finish at the start of chunk 4. **Overlap** means including the last N characters of each chunk at the start of the next one. This creates redundancy but ensures boundary facts appear in at least one complete chunk.
>
> Typical overlap values: 10-20% of chunk size. This project uses 64/512 = 12.5%.

### Context enrichment (`chunker.py:60-64`)

```python
if idx > 0 and title.lower() not in raw.lower():
    raw = f"[Source: {title}]\n\n{raw}"
```

This is a critical RAG optimization. When a document is split into chunks, later chunks may contain only raw data (e.g., a specification table) with no mention of which document they belong to. This makes them impossible to retrieve by document name.

The fix: prepend `[Source: Document Title]` to every chunk that does not already mention the title. Now a search for "MI-T100 temperature" matches the spec table chunk because it contains "MI-T100" in the source prefix.

> **Design note.** This problem is common with tabular data in RAG. A markdown table like `| Parameter | Value | ... | -40C to +125C |` embeds poorly because embedding models are trained on natural language, not pipe-delimited tables. The context prefix mitigates this by giving the embedding model natural-language anchors.

---

## Part 6 -- Vector Store

**Read:** `src/agentprobe/target_agent/vectorstore.py` (full file)

> **Refresher: Embeddings and vector similarity**
>
> An **embedding model** converts text into a dense numeric vector (e.g., 384 dimensions for MiniLM). Texts with similar meaning produce vectors that are close together in this high-dimensional space.
>
> **Cosine similarity** measures how aligned two vectors are (1.0 = identical direction, 0.0 = perpendicular, -1.0 = opposite). ChromaDB uses **L2 distance** (Euclidean distance) by default, where lower = more similar.
>
> A **vector store** is a database optimized for "given this query vector, find the N most similar stored vectors." ChromaDB does this locally without a server, using the `SentenceTransformerEmbeddingFunction` to embed text on the fly.

### How ChromaDB is wired (`vectorstore.py:21-34`)

```python
self._ef = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
self._client = chromadb.PersistentClient(path=str(self._persist_dir))
self._collection = self._client.get_or_create_collection(
    name=collection_name,
    embedding_function=self._ef,
)
```

The embedding function is passed to the collection, so ChromaDB automatically embeds text when you add or query it. You never call the embedding model directly.

### Indexing (`vectorstore.py:40-48`)

```python
self._collection.upsert(
    ids=[c.id for c in batch],
    documents=[c.content for c in batch],
    metadatas=[self._serialise_meta(c) for c in batch],
)
```

`upsert` means "insert or update." Running `agentprobe index` twice on the same corpus updates existing chunks rather than duplicating them.

### Search (`vectorstore.py:54-78`)

The search returns `(Chunk, distance)` pairs. The `Chunk` is reconstructed from stored metadata because ChromaDB only stores flat key-value metadata, not nested objects.

**Try it:**

```bash
source .venv/bin/activate
agentprobe index corpora/sample_corpus
agentprobe info   # See chunk count and document list
```

---

## Part 7 -- Retriever

**Read:** `src/agentprobe/target_agent/retriever.py` (full file)

The Retriever is a thin orchestration layer that combines the chunker and vector store. It provides the public API that the rest of the system uses:

- `index_corpus(dir)` -- chunk all files, add to vector store
- `search(query, top_k)` -- find relevant chunks
- `get_document_metadata(doc_id)` -- pass-through to vector store

> **Design note.** Why have a Retriever at all, if it just delegates? It is the **Facade pattern** -- a simplified interface over two subsystems (chunker + vectorstore). The agent tools call `retriever.search()` without knowing about ChromaDB internals or chunking strategies.

---

## Part 8 -- Agent Tools

**Read:** `src/agentprobe/target_agent/tools.py` (full file)

> **Refresher: Defining tools for an LLM**
>
> To enable tool use, you must tell the LLM what tools exist. Each tool definition includes:
> - **name** -- how the LLM refers to it (e.g., `search_documents`)
> - **description** -- natural language explaining what it does (this is what the LLM reads to decide when to use it)
> - **parameters** -- a JSON Schema describing the arguments
>
> The quality of descriptions directly affects tool-use behavior. Vague descriptions lead to the model calling the wrong tool or passing wrong arguments.

### Tool definitions (`tools.py:12-35`)

Two tools are available to the agent:

1. **`search_documents`** -- semantic search over the corpus, returns top-k chunks with content, scores, and metadata
2. **`get_document_metadata`** -- look up metadata for a specific document by ID

The definitions are stored as `(name, description, json_schema)` tuples -- provider-agnostic. The agent converts them to Anthropic or OpenAI format at call time.

### Tool execution (`tools.py:73-99`)

The `execute()` method is a simple dispatch:

```python
def execute(self, tool_name: str, arguments: dict) -> str:
    if tool_name == "search_documents":
        return self._search_documents(arguments["query"])
    ...
```

Tools return JSON strings. This is important -- LLMs work with text, so tool results are serialized to JSON before being injected into the conversation.

> **Design note.** The tool executor is synchronous even though the agent loop is async. This is intentional: the tools only do local operations (ChromaDB queries), which are fast. Making them async would add complexity without benefit.

---

## Part 9 -- The ReAct Agent Loop

**Read:** `src/agentprobe/target_agent/agent.py` (full file)

This is the core of the target agent. Study it carefully.

> **Refresher: The ReAct pattern**
>
> ReAct (**Reasoning + Acting**) is an agent architecture where the LLM alternates between:
>
> 1. **Reason** -- think about what information it needs
> 2. **Act** -- call a tool to get that information
> 3. **Observe** -- read the tool result
> 4. **Repeat** until it has enough information to answer
>
> In practice, the "reasoning" step is implicit -- the LLM decides whether to call a tool or produce a final text answer based on the conversation so far.
>
> The loop looks like:
> ```
> while not done:
>     response = llm.chat(messages + tools)
>     if response has tool_calls:
>         execute tools, append results to messages
>     else:
>         return response.content   # final answer
> ```
>
> The `max_turns` parameter prevents infinite loops if the model keeps calling tools without converging on an answer.

### The agent loop (`agent.py:54-105`)

```python
async def answer(self, question: str) -> AgentResponse:
    tool_defs = self._build_tool_defs()
    messages = self._initial_messages(question)

    for _ in range(self._max_turns):
        resp = await self._llm.chat(messages, system=self._system_prompt, tools=tool_defs)

        if not resp.tool_calls:          # No tool calls = final answer
            return AgentResponse(answer=resp.content or "", ...)

        # Execute tools, feed results back
        messages = self._append_assistant_turn(messages, resp)
        for tc in resp.tool_calls:
            result = self._tools.execute(tc.name, tc.arguments)
        messages = self._append_tool_results(messages, tool_results)

    # Max turns exceeded
    return AgentResponse(answer="I was unable to formulate a complete answer...")
```

Each iteration:
1. Send the full conversation history + tools to the LLM
2. Check `stop_reason`: if the model produced text without tool calls, we are done
3. If the model called tools: execute them locally, append results to the conversation
4. Repeat with the expanded conversation

### Message threading: Anthropic vs OpenAI (`agent.py:126-168`)

The most complex part of the agent is building correct message histories for each provider.

**Anthropic format** -- assistant turn with mixed content blocks:
```python
# Assistant message with text + tool calls
{"role": "assistant", "content": [
    {"type": "text", "text": "Let me search for that..."},
    {"type": "tool_use", "id": "call_123", "name": "search_documents", "input": {"query": "..."}}
]}
# Tool results -- ALL in a single user message
{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "call_123", "content": "..."}
]}
```

**OpenAI format** -- tool calls as a separate field:
```python
# Assistant message with tool_calls array
{"role": "assistant", "content": "...", "tool_calls": [
    {"id": "call_123", "type": "function", "function": {"name": "search_documents", "arguments": "{...}"}}
]}
# Each tool result is a separate message
{"role": "tool", "tool_call_id": "call_123", "content": "..."}
```

> **Key difference:** Anthropic batches all tool results into one `user` message. OpenAI uses separate `tool` messages. Getting this wrong causes API errors. This was a real bug during development -- sending Anthropic tool results as separate messages caused the agent to loop indefinitely.

### The AgentResponse (`agent.py:14-23`)

The response captures everything needed for auditing:

```python
@dataclass
class AgentResponse:
    answer: str                    # The final text
    sources: list[str]             # Extracted document citations
    tool_calls_log: list[dict]     # Every tool call with full results
    tool_calls_made: int           # How many tools were called
    total_input_tokens: int        # Total tokens consumed
    total_output_tokens: int
    latency_ms: float              # Wall-clock time
```

The `tool_calls_log` records the full result of each tool call (not just a summary). This is essential for the hallucination checker, which needs to compare the agent's answer against the actual chunks it retrieved.

---

## Part 10 -- System Prompt Design

**Read:** `prompts/target_system.md` (full file)

> **Refresher: System prompts as behavioral contracts**
>
> The system prompt is the primary mechanism for controlling an LLM agent's behavior. It is not a suggestion -- it is a contract that defines:
> - **What** the agent should do (answer from documents only)
> - **How** it should do it (cite sources, flag ambiguity)
> - **What not to do** (speculate, use prior knowledge)
> - **When to stop** (tool-use limits, when to give up)
>
> A well-structured system prompt has distinct sections for different concerns. Mixing behavioral rules with formatting instructions makes both harder to follow.

### Structure of the target system prompt

The prompt has three sections:

1. **Tool-use workflow** -- controls the ReAct loop behavior:
   - "Search first, then answer immediately"
   - "Do not exceed 3 tool calls"
   - "Never repeat a search"

2. **Rules** -- behavioral constraints:
   - Answer only from retrieved documents
   - Cite sources
   - Say "I don't know" when appropriate
   - Flag ambiguity and contradictions

3. **Response format** -- output structure

> **Design note.** The "tool-use workflow" section was added to fix a real bug: without it, the model would search repeatedly with rephrased queries, never producing a final answer. The `max_turns` limit in the agent loop is a hard safety net, but the system prompt is the soft control that actually guides the model toward convergence.

**Try it:**

```bash
source .venv/bin/activate
# A factual question -- should search once, answer immediately
agentprobe ask "What is the temperature range of the MI-T100?"
# An out-of-scope question -- should search, then refuse
agentprobe ask "What is the capital of France?"
```

---

## Part 11 -- Probe Taxonomy

**Read:** `src/agentprobe/auditor/probes.py` (full file)

> **Refresher: Systematic agent evaluation**
>
> Testing an LLM agent with a handful of manual questions is not sufficient. Different failure modes require different test strategies:
> - A factual question tests **accuracy**
> - An out-of-scope question tests **refusal behavior**
> - An adversarial question tests **robustness**
>
> A **probe** is a structured test case with a question, expected behavior, and optional ground truth. Probes are organized into **categories** that target specific weaknesses. This approach is inspired by software testing practices (unit tests, edge cases, fuzz testing) applied to LLM behavior.

### The seven categories

| Category | What it tests | Expected agent behavior |
|----------|---------------|------------------------|
| P1 Factual | Can it answer correctly? | Correct answer with citations |
| P2 Out-of-scope | Does it know what it doesn't know? | Refusal ("I don't know") |
| P3 Ambiguous | Does it recognize unclear questions? | Flag the ambiguity |
| P4 Contradiction | Does it detect conflicting sources? | Report the conflict |
| P5 Composite | Can it synthesize across documents? | Multi-source answer |
| P6 Adversarial | Does misleading framing fool it? | Same correct answer as P1 |
| P7 Certainty | Is its confidence calibrated? | Appropriate confidence expression |

### Category dependencies

P6 and P7 depend on P1: adversarial probes are reformulations of factual questions, and certainty probes are follow-ups to them. The generator always produces P1 first (`test_generator.py:45-69`).

### The Probe dataclass (`probes.py:53-78`)

```python
@dataclass
class Probe:
    id: str                      # e.g., "P1_a432666a"
    category: str                # "P1" through "P7"
    question: str                # The actual question
    expected_behavior: str       # "correct_answer", "refusal", etc.
    ground_truth: str | None     # Expected answer (for P1, P5, P6)
    difficulty: str              # "easy", "medium", "hard"
    metadata: dict               # Category-specific extra data
```

---

## Part 12 -- LLM-Powered Probe Generation

**Read:** `src/agentprobe/auditor/test_generator.py` (full file)

> **Refresher: Using LLMs to generate test cases**
>
> Instead of hand-writing hundreds of test questions, you can use an LLM to generate them from the corpus. The pattern:
> 1. Sample chunks from the corpus
> 2. Prompt the LLM: "Given these excerpts, generate N factual questions with answers"
> 3. Parse the structured JSON output
> 4. Wrap each item in a Probe object
>
> This is **meta-use** of an LLM -- using one model to create tests for another. The generator LLM and the target LLM can (and should) be independent to avoid self-reinforcing blind spots.

### Generation strategy per category

Each category has a tailored generation prompt:

- **P1** (`test_generator.py:77-109`): Feed corpus chunks, ask for factual Q&A pairs
- **P2** (`test_generator.py:111-143`): Feed document summaries, ask for plausible but out-of-scope questions
- **P3** (`test_generator.py:145-174`): Feed chunks, ask for genuinely ambiguous questions
- **P4** (`test_generator.py:176-213`): Feed chunks from different documents, ask for contradiction-exposing questions
- **P5** (`test_generator.py:215-249`): Feed multi-document chunks, ask for synthesis questions
- **P6** (`test_generator.py:251-292`): Feed P1 Q&A pairs, ask for adversarial reformulations
- **P7** (`test_generator.py:294-336`): Feed P1 questions, ask for confidence-probing follow-ups

### Structured output parsing (`test_generator.py:379-398`)

The LLM is instructed to output JSON arrays. The parser is defensive:

```python
@staticmethod
def _parse_json_array(text: str) -> list[dict]:
    text = re.sub(r"^```(?:json)?\s*", "", text)   # Strip markdown fences
    text = re.sub(r"\s*```$", "", text)
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass
    # Fallback: find array in text
    match = re.search(r"\[.*\]", text, re.DOTALL)
    ...
```

> **Design note.** LLMs often wrap JSON in markdown code fences (` ```json ... ``` `) even when asked not to. The system prompt says "Output only valid JSON arrays. No markdown fences, no commentary" but you cannot fully trust this. The parser handles common deviations.

### Temperature for generation (`test_generator.py:347`)

```python
resp = await self._llm.chat([...], system="...", temperature=0.7)
```

The generator uses `temperature=0.7` for diverse probe generation, while the target agent and evaluator use `temperature=0.0` for deterministic answers. This is a deliberate asymmetry -- you want varied test cases but reproducible evaluations.

---

## Part 13 -- Evaluation

**Read:** `src/agentprobe/auditor/evaluator.py` (full file)

### Two-tier evaluation

> **Refresher: Automatic evaluation vs. LLM-as-judge**
>
> **Automatic evaluation** uses pattern matching and heuristics -- fast, free, deterministic, but brittle. It works well for binary checks (did the agent refuse? did it mention a specific number?) but fails on nuance.
>
> **LLM-as-judge** sends the question + answer + ground truth to a separate LLM and asks it to score the response. This is more expensive (one API call per evaluation) but captures nuance that regex cannot.
>
> The standard approach is to use automatic evaluation as the primary method and fall back to LLM-as-judge for uncertain cases. This is exactly what agentprobe does.

### Automatic evaluation strategies

Each category has a tailored heuristic:

| Category | Strategy | Implementation |
|----------|----------|---------------|
| P1 | Extract key tokens (numbers, units, model names) from ground truth, check if they appear in the answer | `_extract_key_tokens()` + substring matching |
| P2 | Match against refusal patterns ("I don't know", "not covered", etc.) | `_REFUSAL_PATTERNS` list |
| P3 | Match against ambiguity patterns ("ambiguous", "could mean", "clarification") | `_AMBIGUITY_PATTERNS` list |
| P4 | Match against contradiction patterns ("conflicting", "inconsistent", "discrepancy") | `_CONTRADICTION_PATTERNS` list |
| P5 | Count distinct document sources cited in the answer | `_count_sources()` |
| P6 | Same as P1 (correct answer despite misleading framing) | Delegates to `_eval_p1` |
| P7 | Detect confidence expressions ("8/10", "quite confident", "sure") | Regex for numeric + qualitative confidence |

### The LLM-as-judge (`evaluator.py:239-318`)

The judge receives a structured prompt:

```
## Probe
- Category: P7
- Question: What is the MI-T100 accuracy? How confident are you?
- Expected behavior: calibrated_confidence
- Ground truth: (not available)

## Agent's response
[the actual answer]

## Instructions
Score the response from 0.0 to 1.0. Output JSON only.
```

And returns:
```json
{"score": 0.2, "passed": false, "reasoning": "Agent answered but did not calibrate confidence"}
```

### When the judge overrides (`auditor.py:203-206`)

```python
eval_result = self._auto_eval.evaluate(probe, agent_resp.answer)
if self._llm_judge:
    llm_eval = await self._llm_judge.evaluate(probe, agent_resp.answer)
    if 0.3 <= eval_result.score <= 0.7:
        eval_result = llm_eval
```

The LLM judge only overrides when the automatic evaluator is uncertain (score between 0.3 and 0.7). If auto-eval is confident (0.0 or 1.0), the judge result is discarded. This saves API calls while using the judge where it matters most.

---

## Part 14 -- Hallucination Detection

**Read:** `src/agentprobe/auditor/hallucination.py` (full file)

> **Refresher: Hallucination in RAG agents**
>
> A **hallucination** is when the agent states something that is not supported by its retrieved sources. There are two kinds:
>
> 1. **Ungrounded claims** -- the agent says something that does not appear in any retrieved chunk. It may be true in the real world but is not traceable to the corpus.
> 2. **Factual errors** -- the agent states something that contradicts the retrieved chunks or the known ground truth.
>
> Detecting hallucinations is one of the hardest problems in LLM evaluation. agentprobe uses an embedding-based approach rather than an LLM-based one, which is cheaper but less nuanced.

### Pass 1: Grounding check (`hallucination.py:104-127`)

The grounding check uses **cosine similarity between claim embeddings and chunk embeddings**:

```python
claim_embs = self._model.encode(claims, normalize_embeddings=True)
chunk_embs = self._model.encode(chunks, normalize_embeddings=True)

sim_matrix = claim_embs @ chunk_embs.T       # (n_claims, n_chunks) similarity matrix
best_sim = sim_matrix.max(axis=1)            # best chunk match per claim
```

For each claim, find the most similar retrieved chunk. If the similarity is below the threshold (0.65 = `1.0 - 0.35`), the claim is flagged as ungrounded.

> **Design note.** The matrix multiply `claim_embs @ chunk_embs.T` computes all pairwise cosine similarities at once (since vectors are L2-normalized, dot product = cosine similarity). This is much faster than comparing pairs individually.

### Claim extraction (`hallucination.py:171-191`)

Before checking grounding, the answer must be split into individual claims. The `_split_claims` method:

1. Strips the "Sources:" section (not a factual claim)
2. Splits on sentence boundaries
3. Filters out sentences shorter than 20 characters
4. Filters out **non-claim patterns** -- refusal phrases and meta-commentary

The non-claim filter (`hallucination.py:157-169`) is critical:

```python
_NON_CLAIM_PATTERNS = re.compile(
    r"(?i)"
    r"(?:based on (?:the|my) (?:search|retrieved))"
    r"|(?:I (?:don'?t know|was unable|cannot|could not|...))"
    r"|(?:the (?:available |retrieved )?documentation (?:does not|focuses|...))"
    ...
)
```

Without this filter, sentences like "Based on the search results, I found the information" would be flagged as hallucinations (they have low similarity to any corpus chunk because they are meta-commentary, not factual claims).

### Pass 2: Factual check (`hallucination.py:133-150`)

If `ground_truth` is available, extract key facts (numbers, units, model numbers) and verify they appear in the answer. Missing facts contribute a penalty to the final score.

### Connecting it to the agent (`hallucination.py:205-223`)

The `extract_retrieved_chunks()` function parses the agent's `tool_calls_log` to recover the actual text chunks the agent retrieved. This is compared against the agent's answer -- checking whether the answer is grounded in what the agent *actually saw*, not the entire corpus.

---

## Part 15 -- Metrics Aggregation

**Read:** `src/agentprobe/auditor/metrics.py` (full file)

The `AuditMetrics.compute()` classmethod takes raw evaluation results, hallucination results, and agent stats, and produces a single metrics object with:

- Per-category scores (average score per P1-P7)
- Hallucination rate (fraction of probes flagged)
- Groundedness score (average grounding score)
- Average latency and tool calls
- Failure breakdown by category

This is a pure data-aggregation module -- no LLM calls, no complex logic.

---

## Part 16 -- Audit Orchestrator

**Read:** `src/agentprobe/auditor/auditor.py` (full file)

The `Auditor` class ties everything together in a three-phase pipeline:

### Phase 1: Generate probes (`auditor.py:164-165`)

```python
probes = await self._generator.generate(cats)
```

Calls the test generator for each requested category.

### Phase 2: Execute probes with concurrency control (`auditor.py:167-179`)

```python
sem = asyncio.Semaphore(self._concurrency)

async def _run_single(idx, probe):
    async with sem:
        result = await self._execute_probe(probe)
        ...

tasks = [_run_single(i, p) for i, p in enumerate(probes)]
audit.probe_results = await asyncio.gather(*tasks)
```

> **Refresher: Concurrency control with semaphores**
>
> `asyncio.gather()` launches all probe executions concurrently. Without a limit, 35 probes would fire 35+ API calls simultaneously, hitting rate limits immediately.
>
> An `asyncio.Semaphore(n)` acts as a counter: at most `n` coroutines can hold it at once. Others wait. With `concurrency=1`, probes run sequentially; with `concurrency=5`, up to 5 run in parallel.
>
> The right value depends on your API rate limit. At 30K input tokens/minute with ~5K tokens per probe, `concurrency=1` or `2` is safe.

### Phase 3: Compute metrics (`auditor.py:181-192`)

Aggregates all results into `AuditMetrics`.

### The `_execute_probe` pipeline (`auditor.py:196-223`)

For each probe, three steps run in sequence:

1. **Agent execution** -- run the target agent on the probe question
2. **Evaluation** -- automatic eval, then LLM judge if uncertain
3. **Hallucination check** -- compare answer against retrieved chunks

### Run persistence (`auditor.py:88-99`)

The full audit (probes, responses, evaluations, hallucination results, metrics) is serialized to JSON. This enables:
- Report generation from saved data (`agentprobe report <run_id>`)
- Comparison between runs (`agentprobe compare <run_a> <run_b>`)

---

## Part 17 -- Report Generation

**Read:** `src/agentprobe/report/generator.py` (full file)

The report generator produces self-contained HTML or Markdown from an `AuditRun`. Key sections:

### Overall reliability score (`generator.py:69-93`)

A weighted composite of all category scores:

```python
weights = {
    "accuracy_p1": 0.25,          # Heaviest -- baseline correctness
    "adversarial_robustness_p6": 0.15,
    "refusal_rate_p2": 0.15,
    ...
}
score *= 1.0 - (hallucination_rate * 0.5)  # Hallucination penalty
```

The weights reflect the relative importance of each category. P1 (factual accuracy) is weighted highest because a RAG agent that cannot answer factual questions correctly has a fundamental problem.

### Recommendations engine (`generator.py:108-131`)

Threshold-driven recommendations:

```python
if m.accuracy_p1 < t.get("accuracy_min", 0.85):
    recs.append("Factual accuracy is below threshold. Consider improving...")
if m.hallucination_rate > t.get("hallucination_max", 0.10):
    recs.append("Hallucination rate exceeds threshold. Add a post-generation grounding check...")
```

Each recommendation is actionable and tied to a specific metric violation.

### Self-contained HTML (`generator.py:384-525`)

The HTML report embeds all CSS inline -- no external dependencies. This means it works as a standalone file that can be emailed, shared, or opened anywhere.

---

## Part 18 -- CLI

**Read:** `src/agentprobe/cli.py` (full file)

The CLI uses Click and acts as the integration layer that wires all components together from configuration.

### Environment variable management (`cli.py:14`)

```python
load_dotenv()
```

This loads the `.env` file at import time, making `ANTHROPIC_API_KEY` available as an environment variable. The Anthropic and OpenAI SDKs automatically read their respective API keys from the environment -- no explicit key passing needed.

### Component assembly (`cli.py:27-76`)

The `_build_retriever()` and `_build_agent()` functions construct the component graph from config:

```
config.toml → _build_retriever() → Retriever(VectorStore, DocumentChunker)
                                       ↓
           → _build_agent() → TargetAgent(LLMProvider, Retriever, system_prompt)
```

This is the **Composition Root** pattern -- all dependencies are assembled at the top level (the CLI), and inner modules never construct their own dependencies.

---

## Part 19 -- Test Suite

**Read:** `tests/conftest.py`, then any test file

### Test philosophy

The test suite (93 tests) is designed to run **without API keys**. No test makes a real LLM call. This means:

- Unit tests cover chunking, evaluation heuristics, metrics, and report generation
- Integration tests cover the retriever pipeline (chunker + ChromaDB, which runs locally)
- The agent loop and auditor orchestration are not tested end-to-end (would require API calls)

### The mock audit fixture (`conftest.py:80-206`)

The `mock_audit_run` fixture creates a realistic `AuditRun` with 21 probe results across all 7 categories, including:
- Passing and failing probes per category
- Hallucinated and grounded responses
- Realistic token counts and latencies

This is used by every report test. The fixture uses `random.seed(42)` for deterministic "random" values.

### Key testing patterns

**Temporary directories** (`test_retriever.py:13-28`): Tests that need ChromaDB or corpus files use pytest's `tmp_path` fixture, which creates a fresh temporary directory per test.

**Module-scoped fixtures** (`test_hallucination.py:15`): The `HallucinationChecker` loads a sentence-transformer model (~80MB). Using `scope="module"` loads it once for all tests in the file, not once per test.

**Testing evaluation heuristics** (`test_evaluator.py`): Each evaluator category is tested with a passing and failing example. The tests verify that the regex patterns correctly detect refusal phrases, ambiguity flags, contradiction language, and confidence expressions.

**Try it:**

```bash
source .venv/bin/activate
pytest tests/ -v             # Run all 93 tests
pytest tests/test_evaluator.py -v  # Just evaluation tests
```

---

## Concept Index

| Concept | First explained in |
|---------|--------------------|
| Agent tools / function calling | Part 2 (LLM Provider Abstraction) |
| Automatic evaluation (heuristic) | Part 13 (Evaluation) |
| Chunk overlap | Part 5 (Document Chunking) |
| Chunking for RAG | Part 5 (Document Chunking) |
| Concurrency control (semaphores) | Part 16 (Audit Orchestrator) |
| Context enrichment (chunk prefixing) | Part 5 (Document Chunking) |
| Cosine similarity / vector similarity | Part 6 (Vector Store) |
| Embeddings | Part 6 (Vector Store) |
| Grounding check (hallucination) | Part 14 (Hallucination Detection) |
| Hallucination in RAG | Part 14 (Hallucination Detection) |
| LLM-as-judge | Part 13 (Evaluation) |
| LLM-powered test generation | Part 12 (Probe Generation) |
| Message threading (Anthropic vs OpenAI) | Part 9 (ReAct Agent Loop) |
| Probe taxonomy / systematic evaluation | Part 11 (Probe Taxonomy) |
| Provider abstraction (Adapter pattern) | Part 2 (LLM Provider Abstraction) |
| RAG (Retrieval-Augmented Generation) | Part 5 (Document Chunking) |
| Rate limiting and retry | Part 3 (Anthropic Provider) |
| ReAct pattern | Part 9 (ReAct Agent Loop) |
| Structured output parsing | Part 12 (Probe Generation) |
| System prompts as behavioral contracts | Part 10 (System Prompt Design) |
| Temperature (generation vs evaluation) | Part 12 (Probe Generation) |
| Tool result batching (Anthropic) | Part 9 (ReAct Agent Loop) |
| Tool result messages (OpenAI) | Part 4 (OpenAI Provider) |
