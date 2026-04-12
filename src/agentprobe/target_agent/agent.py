"""Target RAG agent with a ReAct-style tool-use loop."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from agentprobe.llm.base import LLMProvider, LLMResponse
from agentprobe.target_agent.retriever import Retriever
from agentprobe.target_agent.tools import AgentTools


@dataclass
class AgentResponse:
    """The agent's final answer plus diagnostics useful for auditing."""

    answer: str
    sources: list[str] = field(default_factory=list)
    tool_calls_log: list[dict] = field(default_factory=list)
    tool_calls_made: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    latency_ms: float = 0.0


class TargetAgent:
    """A simple RAG agent that answers questions grounded in a document corpus.

    The agent uses a ReAct-style loop:
      1. Send user question (+ conversation so far) to the LLM with tools.
      2. If the LLM calls a tool, execute it and append the result.
      3. Repeat until the LLM produces a text response or *max_turns* is hit.
    """

    def __init__(
        self,
        llm: LLMProvider,
        retriever: Retriever,
        system_prompt: str,
        *,
        max_turns: int = 10,
        provider_type: str = "anthropic",
    ):
        self._llm = llm
        self._tools = AgentTools(retriever)
        self._system_prompt = system_prompt
        self._max_turns = max_turns
        self._provider_type = provider_type

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def answer(self, question: str) -> AgentResponse:
        """Run the agent loop and return the final answer."""
        t0 = time.perf_counter()

        tool_defs = self._build_tool_defs()
        messages = self._initial_messages(question)

        total_in = 0
        total_out = 0
        tool_log: list[dict] = []

        for _ in range(self._max_turns):
            resp: LLMResponse = await self._llm.chat(
                messages,
                system=self._system_prompt,
                tools=tool_defs,
            )
            total_in += resp.usage.input_tokens
            total_out += resp.usage.output_tokens

            # No tool calls → final answer
            if not resp.tool_calls:
                elapsed = (time.perf_counter() - t0) * 1000
                return AgentResponse(
                    answer=resp.content or "",
                    sources=self._extract_sources(resp.content or ""),
                    tool_calls_log=tool_log,
                    tool_calls_made=len(tool_log),
                    total_input_tokens=total_in,
                    total_output_tokens=total_out,
                    latency_ms=elapsed,
                )

            # Execute every tool call and feed results back
            messages = self._append_assistant_turn(messages, resp)
            for tc in resp.tool_calls:
                result = self._tools.execute(tc.name, tc.arguments)
                tool_log.append({"tool": tc.name, "args": tc.arguments, "result": result})
                messages = self._append_tool_result(messages, tc.id, result)

        # Max turns exceeded — return whatever we have
        elapsed = (time.perf_counter() - t0) * 1000
        return AgentResponse(
            answer="I was unable to formulate a complete answer within the allowed number of steps.",
            tool_calls_log=tool_log,
            tool_calls_made=len(tool_log),
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            latency_ms=elapsed,
        )

    # ------------------------------------------------------------------
    # Message construction helpers (provider-aware)
    # ------------------------------------------------------------------

    def _initial_messages(self, question: str) -> list[dict]:
        return [{"role": "user", "content": question}]

    def _build_tool_defs(self) -> list[dict]:
        """Convert agnostic tool definitions into provider-specific format."""
        raw = self._tools.definitions()
        if self._provider_type == "anthropic":
            from agentprobe.llm.anthropic import AnthropicProvider

            return [AnthropicProvider.tool_definition(n, d, s) for n, d, s in raw]
        else:
            from agentprobe.llm.openai import OpenAIProvider

            return [OpenAIProvider.tool_definition(n, d, s) for n, d, s in raw]

    def _append_assistant_turn(self, messages: list[dict], resp: LLMResponse) -> list[dict]:
        """Append the assistant's response (text + tool_use blocks) to the history."""
        if self._provider_type == "anthropic":
            content: list[dict] = []
            if resp.content:
                content.append({"type": "text", "text": resp.content})
            for tc in resp.tool_calls:
                content.append({"type": "tool_use", "id": tc.id, "name": tc.name, "input": tc.arguments})
            messages.append({"role": "assistant", "content": content})
        else:
            msg: dict = {"role": "assistant", "content": resp.content}
            if resp.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": __import__("json").dumps(tc.arguments)},
                    }
                    for tc in resp.tool_calls
                ]
            messages.append(msg)
        return messages

    def _append_tool_result(self, messages: list[dict], tool_call_id: str, result: str) -> list[dict]:
        """Append a tool result to the conversation history."""
        if self._provider_type == "anthropic":
            from agentprobe.llm.anthropic import AnthropicProvider

            messages.append(AnthropicProvider.tool_result_message(tool_call_id, result))
        else:
            from agentprobe.llm.openai import OpenAIProvider

            messages.append(OpenAIProvider.tool_result_message(tool_call_id, result))
        return messages

    # ------------------------------------------------------------------
    # Source extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_sources(text: str) -> list[str]:
        """Pull doc references from parenthetical citations in the answer."""
        import re

        hits = re.findall(r"\(([^)]*(?:Datasheet|Guide|Overview|Notes|FAQ|Reference|Platform|Procedures|Schedule|Protocols|Certifications|Troubleshooting)[^)]*)\)", text, re.IGNORECASE)
        return list(dict.fromkeys(hits))  # dedupe, preserve order
