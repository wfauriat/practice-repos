"""CLI entry point for agentprobe."""

from __future__ import annotations

import asyncio
import json
import sys
import tomllib
from pathlib import Path

import click


def _load_config(path: str | Path) -> dict:
    """Load and return the TOML configuration."""
    p = Path(path)
    if not p.exists():
        click.echo(f"Error: config file not found: {p}", err=True)
        sys.exit(1)
    with open(p, "rb") as f:
        return tomllib.load(f)


def _build_retriever(cfg: dict):
    """Construct a Retriever from config."""
    from agentprobe.target_agent.chunker import DocumentChunker
    from agentprobe.target_agent.retriever import Retriever
    from agentprobe.target_agent.vectorstore import VectorStore

    rag = cfg.get("rag", {})
    chunker = DocumentChunker(
        chunk_size=rag.get("chunk_size", 512),
        chunk_overlap=rag.get("chunk_overlap", 64),
    )
    vs = VectorStore(
        persist_dir=rag.get("persist_dir", ".agentprobe/chromadb"),
        embedding_model=rag.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
    )
    return Retriever(vectorstore=vs, chunker=chunker, top_k=rag.get("top_k", 5))


def _build_agent(cfg: dict, retriever):
    """Construct a TargetAgent from config and an existing retriever."""
    from agentprobe.target_agent.agent import TargetAgent

    target_cfg = cfg.get("target", {})
    provider_type = target_cfg.get("provider", "anthropic")
    model = target_cfg.get("model", "claude-sonnet-4-20250514")

    # Load system prompt
    prompt_file = Path(target_cfg.get("system_prompt_file", "prompts/target_system.md"))
    if prompt_file.exists():
        system_prompt = prompt_file.read_text(encoding="utf-8")
    else:
        system_prompt = "You are a helpful document-grounded assistant."

    # Build LLM provider
    if provider_type == "anthropic":
        from agentprobe.llm.anthropic import AnthropicProvider

        llm = AnthropicProvider(model=model)
    else:
        from agentprobe.llm.openai import OpenAIProvider

        llm = OpenAIProvider(model=model)

    return TargetAgent(
        llm=llm,
        retriever=retriever,
        system_prompt=system_prompt,
        max_turns=target_cfg.get("max_turns", 10),
        provider_type=provider_type,
    )


# ======================================================================
# CLI
# ======================================================================


@click.group()
@click.option("--config", "-c", default="config.toml", help="Path to config.toml")
@click.pass_context
def main(ctx: click.Context, config: str) -> None:
    """agentprobe — systematically audit LLM RAG agents."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["config"] = _load_config(config)


# ----------------------------------------------------------------------
# index
# ----------------------------------------------------------------------


@main.command()
@click.argument("corpus_dir", type=click.Path(exists=True, file_okay=False))
@click.pass_context
def index(ctx: click.Context, corpus_dir: str) -> None:
    """Index a corpus directory into the vector store."""
    cfg = ctx.obj["config"]
    retriever = _build_retriever(cfg)
    click.echo(f"Indexing corpus from {corpus_dir} ...")
    n = retriever.index_corpus(corpus_dir)
    click.echo(f"Done — {n} chunks indexed ({retriever.chunk_count} total in store).")


# ----------------------------------------------------------------------
# ask  (convenience command for testing the target agent)
# ----------------------------------------------------------------------


@main.command()
@click.argument("question")
@click.pass_context
def ask(ctx: click.Context, question: str) -> None:
    """Ask the target agent a question (for manual testing)."""
    cfg = ctx.obj["config"]
    retriever = _build_retriever(cfg)
    agent = _build_agent(cfg, retriever)

    async def _run():
        resp = await agent.answer(question)
        click.echo(resp.answer)
        click.echo(f"\n--- stats ---")
        click.echo(f"Tool calls: {resp.tool_calls_made}")
        click.echo(f"Sources:    {resp.sources}")
        click.echo(f"Latency:    {resp.latency_ms:.0f} ms")
        click.echo(f"Tokens:     {resp.total_input_tokens} in / {resp.total_output_tokens} out")

    asyncio.run(_run())


# ----------------------------------------------------------------------
# info
# ----------------------------------------------------------------------


@main.command()
@click.pass_context
def info(ctx: click.Context) -> None:
    """Show information about the indexed corpus."""
    cfg = ctx.obj["config"]
    retriever = _build_retriever(cfg)
    docs = retriever.list_documents()
    click.echo(f"Total chunks in store: {retriever.chunk_count}")
    click.echo(f"Documents indexed:     {len(docs)}")
    for d in docs:
        click.echo(f"  - {d['doc_id']}: {d['title']} ({d['source_file']})")


# ----------------------------------------------------------------------
# run  (execute an audit)
# ----------------------------------------------------------------------


def _build_llm(provider: str, model: str):
    """Build an LLM provider from type + model name."""
    if provider == "anthropic":
        from agentprobe.llm.anthropic import AnthropicProvider

        return AnthropicProvider(model=model)
    else:
        from agentprobe.llm.openai import OpenAIProvider

        return OpenAIProvider(model=model)


@main.command()
@click.option("--probes", "-p", default="all", help="Probe categories: 'all' or 'P1,P2,...'")
@click.option("--corpus", default="corpora/sample_corpus", help="Path to corpus directory")
@click.option("--output", "-o", default=None, help="Output directory for results (default: from config)")
@click.option("--concurrency", default=5, type=int, help="Max parallel probe executions")
@click.option("--no-llm-judge", is_flag=True, help="Skip LLM-as-judge evaluation (faster)")
@click.pass_context
def run(ctx: click.Context, probes: str, corpus: str, output: str | None, concurrency: int, no_llm_judge: bool) -> None:
    """Run an audit against the target agent."""
    from agentprobe.auditor.auditor import Auditor

    cfg = ctx.obj["config"]
    retriever = _build_retriever(cfg)
    agent = _build_agent(cfg, retriever)

    # Build auditor + evaluator LLMs
    auditor_cfg = cfg.get("auditor", {})
    evaluator_cfg = cfg.get("evaluator", {})
    auditor_llm = _build_llm(
        auditor_cfg.get("provider", "anthropic"),
        auditor_cfg.get("model", "claude-sonnet-4-20250514"),
    )
    evaluator_llm = _build_llm(
        evaluator_cfg.get("provider", "anthropic"),
        evaluator_cfg.get("model", "claude-sonnet-4-20250514"),
    )

    rag_cfg = cfg.get("rag", {})
    auditor = Auditor(
        target_agent=agent,
        auditor_llm=auditor_llm,
        evaluator_llm=evaluator_llm,
        retriever=retriever,
        corpus_dir=corpus,
        probes_per_category=auditor_cfg.get("probes_per_category", 20),
        concurrency=concurrency,
        use_llm_judge=not no_llm_judge,
        embedding_model=rag_cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2"),
    )

    def _progress(done: int, total: int, probe_id: str) -> None:
        click.echo(f"  [{done}/{total}] {probe_id}")

    async def _run():
        click.echo(f"Starting audit (categories: {probes}) ...")
        audit = await auditor.run(
            categories=probes,
            config_snapshot=cfg,
            progress_callback=_progress,
        )

        # Save results
        output_dir = output or cfg.get("output", {}).get("report_dir", "./reports")
        path = audit.save(output_dir)
        click.echo(f"\nResults saved to {path}")

        # Print summary
        click.echo(f"\n{'=' * 50}")
        click.echo(f"AUDIT SUMMARY — {audit.run_id}")
        click.echo(f"{'=' * 50}")
        for line in audit.metrics.summary_lines():
            click.echo(f"  {line}")

    asyncio.run(_run())


# ----------------------------------------------------------------------
# report  (generate report from a run)
# ----------------------------------------------------------------------


@main.command()
@click.argument("run_id")
@click.option("--dir", "report_dir", default="./reports", help="Directory containing run JSON files")
@click.option("--format", "fmt", default=None, help="Report format: 'html' or 'markdown' (default: from config)")
@click.pass_context
def report(ctx: click.Context, run_id: str, report_dir: str, fmt: str | None) -> None:
    """Generate a report from a previous audit run."""
    path = Path(report_dir) / f"{run_id}.json"
    if not path.exists():
        click.echo(f"Error: run file not found: {path}", err=True)
        sys.exit(1)

    from agentprobe.auditor.auditor import AuditRun
    from agentprobe.report.generator import ReportGenerator

    cfg = ctx.obj["config"]
    audit = AuditRun.load(path)
    fmt = fmt or cfg.get("output", {}).get("report_format", "html")
    thresholds = cfg.get("thresholds", {})

    generator = ReportGenerator(thresholds=thresholds)
    report_path = generator.write(audit, report_dir, fmt=fmt)

    click.echo(f"Loaded run {audit.run_id} ({len(audit.probe_results)} probes)")
    click.echo(f"Report written to {report_path}")
    for line in audit.metrics.summary_lines():
        click.echo(f"  {line}")


# ----------------------------------------------------------------------
# compare  (diff two audit runs)
# ----------------------------------------------------------------------


@main.command()
@click.argument("run_id_a")
@click.argument("run_id_b")
@click.option("--dir", "report_dir", default="./reports", help="Directory containing run JSON files")
@click.pass_context
def compare(ctx: click.Context, run_id_a: str, run_id_b: str, report_dir: str) -> None:
    """Compare two audit runs and show metric deltas."""
    from agentprobe.auditor.auditor import AuditRun, compare_runs

    path_a = Path(report_dir) / f"{run_id_a}.json"
    path_b = Path(report_dir) / f"{run_id_b}.json"
    for p in (path_a, path_b):
        if not p.exists():
            click.echo(f"Error: run file not found: {p}", err=True)
            sys.exit(1)

    run_a = AuditRun.load(path_a)
    run_b = AuditRun.load(path_b)
    diff = compare_runs(run_a, run_b)

    click.echo(f"\nComparing: {run_id_a} → {run_id_b}")
    click.echo(f"{'=' * 55}")
    click.echo(f"{'Metric':<30} {'A':>8} {'B':>8} {'Delta':>8}")
    click.echo(f"{'-' * 55}")
    for key, info in diff["deltas"].items():
        va = info["run_a"]
        vb = info["run_b"]
        delta = info["delta"]
        direction = info["direction"]
        marker = "+" if direction == "improved" else "-" if direction == "regressed" else " "
        if isinstance(va, float):
            click.echo(f"  {key:<28} {va:>7.1%} {vb:>7.1%} {marker}{abs(delta):>6.1%}")
        else:
            click.echo(f"  {key:<28} {va:>8} {vb:>8} {marker}{abs(delta):>7}")
