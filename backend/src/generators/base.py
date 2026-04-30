"""Base generator interface for all SynthData generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class CostEstimate:
    """Estimated cost for a data generation job."""

    estimated_tokens: int
    estimated_cost_usd: float
    estimated_time_seconds: int
    breakdown: dict[str, float]


class BaseGenerator(ABC):
    """Abstract base class for synthetic data generators.

    All data generators (tabular, text, audio) must implement this
    interface. Provides a common contract for schema validation,
    cost estimation, and data generation.
    """

    @abstractmethod
    async def generate(
        self,
        schema: dict[str, Any],
        count: int,
        options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate synthetic data based on the provided schema.

        Args:
            schema: Schema definition describing the data structure.
            count: Number of records to generate.
            options: Additional generation options (format, seed, etc.).

        Returns:
            A list of generated data records.
        """

    @abstractmethod
    def validate(self, schema: dict[str, Any]) -> bool:
        """Validate that a schema definition is well-formed.

        Args:
            schema: Schema definition to validate.

        Returns:
            True if the schema is valid, False otherwise.
        """

    @abstractmethod
    def estimate_cost(self, schema: dict[str, Any], count: int) -> CostEstimate:
        """Estimate the cost of generating data for the given schema.

        Args:
            schema: Schema definition describing the data structure.
            count: Number of records to generate.

        Returns:
            A CostEstimate with token, dollar, and time estimates.
        """

    def _build_system_prompt(self) -> str:
        """Return the system prompt for this generator type."""
        return (
            "You are a synthetic data generator. Generate realistic, "
            "privacy-safe data that follows the provided schema exactly."
        )
