"""Text synthetic data generator using Azure OpenAI."""

from __future__ import annotations

import json
import logging
from typing import Any

from .base import BaseGenerator, CostEstimate

logger = logging.getLogger(__name__)

# Approximate tokens per document by type
_TOKENS_BY_DOC_TYPE = {
    "paragraph": 200,
    "email": 300,
    "chat": 500,
    "article": 1000,
}


class TextGenerator(BaseGenerator):
    """Generate synthetic text documents using Azure OpenAI.

    Supports generating paragraphs, emails, chat transcripts, articles,
    and other text formats with configurable domain, tone, and length.
    """

    def __init__(self, openai_client: Any = None) -> None:
        self._client = openai_client

    async def generate(
        self,
        schema: dict[str, Any],
        count: int,
        options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate synthetic text documents.

        Args:
            schema: Dict with text generation parameters:
                    ``document_type``, ``domain``, ``tone``, ``min_length``, ``max_length``.
            count: Number of documents to generate.
            options: Optional dict with ``seed``, ``model``, etc.

        Returns:
            List of dicts with ``id``, ``content``, and ``metadata`` keys.
        """
        options = options or {}
        doc_type = schema.get("document_type", "paragraph")
        domain = schema.get("domain", "general")
        tone = schema.get("tone", "neutral")
        min_length = schema.get("min_length", 100)
        max_length = schema.get("max_length", 1000)

        prompt = self._build_generation_prompt(
            doc_type=doc_type,
            domain=domain,
            tone=tone,
            count=count,
            min_length=min_length,
            max_length=max_length,
        )

        if self._client is None:
            logger.warning("No OpenAI client configured — returning placeholder text")
            return self._generate_placeholder(doc_type, domain, count)

        response = await self._client.chat.completions.create(
            model=options.get("model", "gpt-4o"),
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            seed=options.get("seed"),
        )

        raw = response.choices[0].message.content
        return self._parse_response(raw, count)

    def validate(self, schema: dict[str, Any]) -> bool:
        """Validate text generation schema."""
        doc_type = schema.get("document_type", "paragraph")
        return doc_type in ("paragraph", "email", "chat", "article")

    def estimate_cost(self, schema: dict[str, Any], count: int) -> CostEstimate:
        """Estimate cost based on document type and count."""
        doc_type = schema.get("document_type", "paragraph")
        tokens_per_doc = _TOKENS_BY_DOC_TYPE.get(doc_type, 200)
        total_tokens = tokens_per_doc * count
        cost_usd = total_tokens * 0.000005

        return CostEstimate(
            estimated_tokens=total_tokens,
            estimated_cost_usd=round(cost_usd, 4),
            estimated_time_seconds=max(3, count * 2),
            breakdown={
                "input_tokens": total_tokens // 4,
                "output_tokens": total_tokens * 3 // 4,
            },
        )

    def _build_system_prompt(self) -> str:
        return (
            "You are a synthetic text document generator. Produce realistic, "
            "privacy-safe documents that read naturally. Never include real "
            "names, addresses, or personally identifiable information."
        )

    @staticmethod
    def _build_generation_prompt(
        doc_type: str,
        domain: str,
        tone: str,
        count: int,
        min_length: int,
        max_length: int,
    ) -> str:
        """Build the LLM prompt for text generation."""
        return (
            f"Generate {count} synthetic {doc_type}(s) as a JSON array.\n\n"
            f"Domain: {domain}\n"
            f"Tone: {tone}\n"
            f"Length: {min_length}–{max_length} characters each\n\n"
            "Return a JSON array of objects with keys: "
            '"id" (sequential integer), "content" (the generated text), '
            '"metadata" (object with "domain", "tone", "type").\n'
            "Return ONLY the JSON array, no extra text."
        )

    @staticmethod
    def _parse_response(raw: str, count: int) -> list[dict[str, Any]]:
        """Parse the LLM response into document dicts."""
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
        return []

    @staticmethod
    def _generate_placeholder(
        doc_type: str, domain: str, count: int
    ) -> list[dict[str, Any]]:
        """Return placeholder documents for development."""
        return [
            {
                "id": i + 1,
                "content": (
                    f"This is a synthetic {doc_type} document #{i + 1} "
                    f"in the {domain} domain. It contains realistic but "
                    f"entirely fabricated content for testing purposes."
                ),
                "metadata": {
                    "domain": domain,
                    "tone": "neutral",
                    "type": doc_type,
                },
            }
            for i in range(count)
        ]
