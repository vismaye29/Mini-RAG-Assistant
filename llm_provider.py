"""
LLM Provider — Multi-backend abstraction for language model generation.
Supports OpenAI, Anthropic Claude, and Ollama (local/free).
"""

from abc import ABC, abstractmethod
from typing import Optional

import config


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        """Generate a response given a user prompt and optional system prompt."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is configured and reachable."""
        ...

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name for UI display."""
        ...


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (GPT-4o-mini, GPT-4o, etc.)."""

    def __init__(self, model: str = config.OPENAI_MODEL):
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=config.OPENAI_API_KEY)
        return self._client

    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=config.LLM_MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()

    def is_available(self) -> bool:
        return bool(config.OPENAI_API_KEY)

    @property
    def display_name(self) -> str:
        return f"OpenAI ({self.model})"


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    def __init__(self, model: str = config.ANTHROPIC_MODEL):
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        return self._client

    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        kwargs = {
            "model": self.model,
            "max_tokens": config.LLM_MAX_TOKENS,
            "temperature": config.LLM_TEMPERATURE,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = client.messages.create(**kwargs)
        return response.content[0].text.strip()

    def is_available(self) -> bool:
        return bool(config.ANTHROPIC_API_KEY)

    @property
    def display_name(self) -> str:
        return f"Anthropic ({self.model})"


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider (free, runs on your machine)."""

    def __init__(self, model: str = config.OLLAMA_MODEL):
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            from ollama import Client
            self._client = Client(host=config.OLLAMA_BASE_URL)
        return self._client

    def generate(self, user_prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": config.LLM_TEMPERATURE,
                "num_predict": config.LLM_MAX_TOKENS,
            },
        )
        return response["message"]["content"].strip()

    def is_available(self) -> bool:
        try:
            client = self._get_client()
            client.list()
            return True
        except Exception:
            return False

    @property
    def display_name(self) -> str:
        return f"Ollama ({self.model})"


# ── Factory ──────────────────────────────────────────────────────────────────

PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "ollama": OllamaProvider,
}


def get_provider(provider_name: Optional[str] = None, model: Optional[str] = None) -> LLMProvider:
    """
    Factory to instantiate the requested LLM provider.

    Args:
        provider_name: One of 'openai', 'anthropic', 'ollama'. Defaults to config.LLM_PROVIDER.
        model: Override the default model for the provider.

    Returns:
        An LLMProvider instance.
    """
    name = (provider_name or config.LLM_PROVIDER).lower().strip()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown LLM provider: '{name}'. Choose from: {list(PROVIDERS.keys())}")

    provider_cls = PROVIDERS[name]
    if model:
        return provider_cls(model=model)
    return provider_cls()
