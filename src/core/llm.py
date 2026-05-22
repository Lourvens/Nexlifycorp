"""
LLM configuration and factory for NexlifyCorp.

Provides centralized LLM model creation with configurable
base URL, model selection, and settings.
"""
import os
from typing import Optional

from langchain_anthropic import ChatAnthropic

from src.core.config import get_config

# Default model (fallback if not in config)
DEFAULT_MODEL = "MiniMax-M2.7"


def create_llm(
    model: str | None = None,
    temperature: float = 0,
    base_url: str | None = None,
) -> ChatAnthropic:
    """
    Create a ChatAnthropic LLM instance with settings from config.

    Args:
        model: Model name (default: claude-sonnet-4-6)
        temperature: Sampling temperature (default: 0)
        base_url: Override base URL. If None, uses config.

    Returns:
        Configured ChatAnthropic instance
    """
    # Get API key from environment (required for authentication)
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

    settings = get_config()

    kwargs = {
        "model": model or getattr(settings, 'anthropic_model', None) or DEFAULT_MODEL,
        "temperature": temperature,
        "api_key": api_key,
    }

    # Use provided base_url or fall back to config
    effective_base_url = base_url or getattr(settings, 'anthropic_base_url', None)
    if effective_base_url:
        kwargs["base_url"] = effective_base_url

    print(f"Creating LLM with base_url: {effective_base_url}")
    return ChatAnthropic(**kwargs)


# Singleton for reuse
_llm: Optional[ChatAnthropic] = None


def get_llm(
    model: str | None = None,
    temperature: float = 0,
    base_url: str | None = None,
) -> ChatAnthropic:
    """
    Get or create a shared LLM instance.

    Uses the same model/temperature/base_url across calls unless
    parameters differ.

    Returns:
        ChatAnthropic instance
    """
    global _llm

    if _llm is None:
        _llm = create_llm(model=model, temperature=temperature, base_url=base_url)
    return _llm


def reset_llm() -> None:
    """Reset the singleton LLM instance."""
    global _llm
    _llm = None
