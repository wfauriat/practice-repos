"""Abstract base for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ToolCall:
    """A tool invocation requested by the LLM."""

    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class TokenUsage:
    """Token counts for a single LLM call."""

    input_tokens: int = 0
    output_tokens: int = 0


@dataclass(frozen=True)
class LLMResponse:
    """Normalized response from any LLM provider."""

    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: TokenUsage = field(default_factory=TokenUsage)
    stop_reason: str = "end_turn"


class LLMProvider(ABC):
    """Unified interface for Anthropic / OpenAI chat + tool-use APIs."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict],
        *,
        system: str | None = None,
        tools: list[dict] | None = None,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Send a chat request and return a normalised response.

        Parameters
        ----------
        messages:
            Conversation history in the provider's native message format.
        system:
            Optional system prompt.
        tools:
            Tool definitions (provider-specific schema).
        temperature:
            Sampling temperature.
        """
