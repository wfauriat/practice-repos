"""OpenAI provider."""

from __future__ import annotations

import json

from openai import AsyncOpenAI

from agentprobe.llm.base import LLMProvider, LLMResponse, TokenUsage, ToolCall


class OpenAIProvider(LLMProvider):
    """LLM provider backed by the OpenAI Chat Completions API."""

    def __init__(self, model: str = "gpt-4o", max_tokens: int = 4096):
        self._client = AsyncOpenAI()
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
        # OpenAI uses a system message as the first message
        full_messages: list[dict] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        kwargs: dict = dict(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=full_messages,
            temperature=temperature,
        )
        if tools:
            kwargs["tools"] = tools

        resp = await self._client.chat.completions.create(**kwargs)
        return self._normalise(resp)

    # ------------------------------------------------------------------
    @staticmethod
    def _normalise(resp) -> LLMResponse:  # noqa: ANN001
        choice = resp.choices[0]
        msg = choice.message

        tool_calls: list[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )

        usage = resp.usage
        return LLMResponse(
            content=msg.content,
            tool_calls=tool_calls,
            usage=TokenUsage(
                input_tokens=usage.prompt_tokens if usage else 0,
                output_tokens=usage.completion_tokens if usage else 0,
            ),
            stop_reason=choice.finish_reason or "stop",
        )

    # ------------------------------------------------------------------
    # Helpers for building OpenAI-format tool definitions
    # ------------------------------------------------------------------
    @staticmethod
    def tool_definition(name: str, description: str, parameters: dict) -> dict:
        """Build an OpenAI-format tool definition."""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }

    @staticmethod
    def tool_result_message(tool_call_id: str, result: str) -> dict:
        """Build the message that delivers a tool result back to GPT."""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result,
        }
