"""
LLM configuration and factory for NexlifyCorp.

Provides centralized LLM model creation with configurable
base URL, model selection, and settings.
"""
import logging
import os
from typing import Optional

from langchain_anthropic import ChatAnthropic

from src.core.config import get_config

logger = logging.getLogger(__name__)

# Default model (fallback if not in config)
DEFAULT_MODEL = "MiniMax-M2.7"
DEFAULT_FAST_MODEL = "claude-haiku-4.5"


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

    logger.info(f"Creating LLM with base_url: {effective_base_url}")
    return ChatAnthropic(**kwargs)


def create_fast_llm(
    model: str | None = None,
    temperature: float = 0,
    base_url: str | None = None,
) -> ChatAnthropic:
    """
    Create a fast ChatAnthropic LLM instance (Haiku) for lightweight tasks.

    Use for: routing classifiers, quick judgments, high-volume low-cost tasks.

    Args:
        model: Model name (default: claude-haiku-4.5)
        temperature: Sampling temperature (default: 0)
        base_url: Override base URL. If None, uses config.

    Returns:
        Configured ChatAnthropic Haiku instance
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable must be set")

    settings = get_config()

    kwargs = {
        "model": model or getattr(settings, 'anthropic_fast_model', None) or DEFAULT_FAST_MODEL,
        "temperature": temperature,
        "api_key": api_key,
    }

    effective_base_url = base_url or getattr(settings, 'anthropic_base_url', None)
    if effective_base_url:
        kwargs["base_url"] = effective_base_url

    logger.info(f"Creating fast LLM (base_url: {effective_base_url})")
    return ChatAnthropic(**kwargs)


# Singleton for reuse
_llm: Optional[ChatAnthropic] = None
_fast_llm: Optional[ChatAnthropic] = None


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


def get_fast_llm(
    model: str | None = None,
    temperature: float = 0,
    base_url: str | None = None,
) -> ChatAnthropic:
    """
    Get or create a shared fast LLM instance (Haiku).

    Use for: routing classifiers, quick judgments, high-volume low-cost tasks.
    Shares the same singleton pattern as get_llm but with a separate instance.

    Returns:
        ChatAnthropic Haiku instance
    """
    global _fast_llm

    if _fast_llm is None:
        _fast_llm = create_fast_llm(model=model, temperature=temperature, base_url=base_url)
    return _fast_llm


def reset_llm() -> None:
    """Reset the singleton LLM instances."""
    global _llm, _fast_llm
    _llm = None
    _fast_llm = None
