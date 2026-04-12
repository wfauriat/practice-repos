"""CLI entry point for agentprobe."""

from __future__ import annotations

import asyncio
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
