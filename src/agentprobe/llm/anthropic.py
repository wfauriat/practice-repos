"""Anthropic Claude provider."""

from __future__ import annotations

import json

from anthropic import AsyncAnthropic

from agentprobe.llm.base import LLMProvider, LLMResponse, TokenUsage, ToolCall


class AnthropicProvider(LLMProvider):
    """LLM provider backed by the Anthropic Messages API."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", max_tokens: int = 4096):
        self._client = AsyncAnthropic()
        self._model = model
        self._max_tokens = max_tokens

    async def chat(
        self,
        messages: list[dict],
        *,
        system: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        kwargs: dict = dict(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=messages,
            temperature=temperature,
        )
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools

        resp = await self._client.messages.create(**kwargs)
        return self._normalise(resp)

    # ------------------------------------------------------------------
    @staticmethod
    def _normalise(resp) -> LLMResponse:  # noqa: ANN001
        content_text: str | None = None
        tool_calls: list[ToolCall] = []

        for block in resp.content:
            if block.type == "text":
                content_text = block.text
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input if isinstance(block.input, dict) else json.loads(block.input),
                    )
                )

        return LLMResponse(
            content=content_text,
            tool_calls=tool_calls,
            usage=TokenUsage(
                input_tokens=resp.usage.input_tokens,
                output_tokens=resp.usage.output_tokens,
            ),
            stop_reason=resp.stop_reason,
        )

    # ------------------------------------------------------------------
    # Helpers for building Anthropic-format tool definitions
    # ------------------------------------------------------------------
    @staticmethod
    def tool_definition(name: str, description: str, parameters: dict) -> dict:
        """Build an Anthropic-format tool definition."""
        return {
            "name": name,
            "description": description,
            "input_schema": parameters,
        }

    @staticmethod
    def tool_result_message(tool_call_id: str, result: str) -> dict:
        """Build the user message that delivers a tool result back to Claude."""
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": result,
                }
            ],
        }
