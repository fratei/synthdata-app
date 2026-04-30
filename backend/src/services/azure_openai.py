"""Azure OpenAI service integration for SynthData."""

from __future__ import annotations

import logging
from typing import Any

from openai import AsyncAzureOpenAI

from ..config import get_settings

logger = logging.getLogger(__name__)


def get_openai_client() -> AsyncAzureOpenAI | None:
    """Create an Azure OpenAI async client from environment config.

    Returns None if credentials are not configured.
    """
    settings = get_settings()

    if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_API_KEY:
        logger.warning(
            "Azure OpenAI not configured — set AZURE_OPENAI_ENDPOINT and "
            "AZURE_OPENAI_API_KEY environment variables"
        )
        return None

    return AsyncAzureOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )


async def generate_completion(
    client: AsyncAzureOpenAI,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.8,
    max_tokens: int | None = None,
    seed: int | None = None,
) -> str:
    """Send a chat completion request to Azure OpenAI.

    Args:
        client: Configured AsyncAzureOpenAI client.
        system_prompt: System-level instruction.
        user_prompt: User query / generation prompt.
        temperature: Sampling temperature (0.0–2.0).
        max_tokens: Optional max tokens in the response.
        seed: Optional seed for reproducibility.

    Returns:
        The assistant's response text.
    """
    settings = get_settings()

    kwargs: dict[str, Any] = {
        "model": settings.AZURE_OPENAI_DEPLOYMENT,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if seed is not None:
        kwargs["seed"] = seed

    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""
