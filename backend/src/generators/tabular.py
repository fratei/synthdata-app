"""Tabular synthetic data generator using Azure OpenAI."""

from __future__ import annotations

import json
import logging
from typing import Any

from .base import BaseGenerator, CostEstimate

logger = logging.getLogger(__name__)

# Approximate tokens per row for cost estimation
_TOKENS_PER_COLUMN = 15


class TabularGenerator(BaseGenerator):
    """Generate synthetic tabular data using Azure OpenAI.

    Takes a schema definition with column names, types, and constraints,
    then uses GPT-4o to produce realistic, privacy-safe rows. Supports
    output as JSON or CSV.
    """

    def __init__(self, openai_client: Any = None) -> None:
        self._client = openai_client

    async def generate(
        self,
        schema: dict[str, Any],
        count: int,
        options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate synthetic tabular data rows.

        Args:
            schema: Dict with a ``columns`` key listing column definitions.
                    Each column has ``name``, ``type``, and optional constraints.
            count: Number of rows to generate.
            options: Optional dict with ``output_format`` (json|csv), ``seed``, etc.

        Returns:
            List of dicts, each representing a generated row.
        """
        options = options or {}
        columns = schema.get("columns", [])

        prompt = self._build_generation_prompt(columns, count)

        # In production, call Azure OpenAI here.
        # For now, return placeholder data to keep the module importable.
        if self._client is None:
            logger.warning("No OpenAI client configured — returning placeholder data")
            return self._generate_placeholder(columns, count)

        response = await self._client.chat.completions.create(
            model=options.get("model", "gpt-4o"),
            messages=[
                {"role": "system", "content": self._build_system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            seed=options.get("seed"),
        )

        raw = response.choices[0].message.content
        return self._parse_response(raw, columns)

    def validate(self, schema: dict[str, Any]) -> bool:
        """Validate that the schema has well-formed column definitions."""
        columns = schema.get("columns")
        if not columns or not isinstance(columns, list):
            return False
        for col in columns:
            if "name" not in col or "type" not in col:
                return False
        return True

    def estimate_cost(self, schema: dict[str, Any], count: int) -> CostEstimate:
        """Estimate cost based on column count and row count."""
        num_columns = len(schema.get("columns", []))
        tokens = num_columns * _TOKENS_PER_COLUMN * count
        cost_usd = tokens * 0.000005  # approximate GPT-4o pricing
        time_seconds = max(2, count // 50)

        return CostEstimate(
            estimated_tokens=tokens,
            estimated_cost_usd=round(cost_usd, 4),
            estimated_time_seconds=time_seconds,
            breakdown={
                "input_tokens": tokens // 3,
                "output_tokens": tokens * 2 // 3,
            },
        )

    def _build_generation_prompt(
        self, columns: list[dict[str, Any]], count: int
    ) -> str:
        """Build the LLM prompt for tabular data generation."""
        col_descriptions = []
        for col in columns:
            desc = f"- {col['name']} ({col['type']})"
            if "min" in col:
                desc += f", min={col['min']}"
            if "max" in col:
                desc += f", max={col['max']}"
            if "values" in col:
                desc += f", allowed={col['values']}"
            col_descriptions.append(desc)

        return (
            f"Generate {count} rows of realistic synthetic data as a JSON array.\n\n"
            f"Columns:\n" + "\n".join(col_descriptions) + "\n\n"
            "Requirements:\n"
            "- Data must look realistic but contain no real PII\n"
            "- Respect all type constraints and value ranges\n"
            "- Return ONLY a JSON array of objects, no extra text\n"
        )

    def _parse_response(
        self, raw: str, columns: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse the LLM response into a list of row dicts."""
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
        return []

    @staticmethod
    def _generate_placeholder(
        columns: list[dict[str, Any]], count: int
    ) -> list[dict[str, Any]]:
        """Return deterministic placeholder rows for development."""
        rows = []
        for i in range(count):
            row = {}
            for col in columns:
                col_type = col.get("type", "string")
                if col_type in ("integer", "int"):
                    row[col["name"]] = i + 1
                elif col_type == "float":
                    row[col["name"]] = round((i + 1) * 1.1, 2)
                elif col_type == "email":
                    row[col["name"]] = f"user{i + 1}@example.com"
                elif col_type == "uuid":
                    row[col["name"]] = f"00000000-0000-0000-0000-{i + 1:012d}"
                elif col_type == "boolean":
                    row[col["name"]] = i % 2 == 0
                else:
                    row[col["name"]] = f"{col['name']}_{i + 1}"
            rows.append(row)
        return rows
