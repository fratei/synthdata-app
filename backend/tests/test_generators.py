"""Tests for SynthData generators."""

from __future__ import annotations

import pytest

from src.generators.base import CostEstimate
from src.generators.tabular import TabularGenerator
from src.generators.text import TextGenerator
from src.generators.audio import AudioGenerator


class TestTabularGenerator:
    """Tests for TabularGenerator."""

    def setup_method(self):
        self.generator = TabularGenerator()

    def test_validate_valid_schema(self):
        schema = {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert self.generator.validate(schema) is True

    def test_validate_invalid_schema_missing_columns(self):
        assert self.generator.validate({}) is False

    def test_validate_invalid_schema_missing_name(self):
        schema = {"columns": [{"type": "string"}]}
        assert self.generator.validate(schema) is False

    def test_estimate_cost(self):
        schema = {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
                {"name": "email", "type": "email"},
            ]
        }
        estimate = self.generator.estimate_cost(schema, 100)
        assert isinstance(estimate, CostEstimate)
        assert estimate.estimated_tokens > 0
        assert estimate.estimated_cost_usd > 0

    @pytest.mark.asyncio
    async def test_generate_placeholder(self):
        schema = {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        results = await self.generator.generate(schema, 5)
        assert len(results) == 5
        assert results[0]["id"] == 1
        assert results[0]["name"] == "name_1"


class TestTextGenerator:
    """Tests for TextGenerator."""

    def setup_method(self):
        self.generator = TextGenerator()

    def test_validate_valid_schema(self):
        schema = {"document_type": "email"}
        assert self.generator.validate(schema) is True

    def test_validate_invalid_schema(self):
        schema = {"document_type": "unknown"}
        assert self.generator.validate(schema) is False

    def test_estimate_cost(self):
        schema = {"document_type": "email"}
        estimate = self.generator.estimate_cost(schema, 10)
        assert isinstance(estimate, CostEstimate)
        assert estimate.estimated_tokens == 3000

    @pytest.mark.asyncio
    async def test_generate_placeholder(self):
        schema = {"document_type": "email", "domain": "healthcare"}
        results = await self.generator.generate(schema, 3)
        assert len(results) == 3
        assert "healthcare" in results[0]["content"]


class TestAudioGenerator:
    """Tests for AudioGenerator."""

    def setup_method(self):
        self.generator = AudioGenerator()

    def test_validate_valid_schema(self):
        schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 2}
        assert self.generator.validate(schema) is True

    def test_validate_invalid_voice(self):
        schema = {"voice": "invalid-voice", "format": "wav", "speakers": 1}
        assert self.generator.validate(schema) is False

    def test_validate_invalid_format(self):
        schema = {"voice": "en-US-JennyNeural", "format": "aac", "speakers": 1}
        assert self.generator.validate(schema) is False

    def test_estimate_cost(self):
        estimate = self.generator.estimate_cost({}, 10)
        assert isinstance(estimate, CostEstimate)
        assert estimate.estimated_cost_usd > 0

    @pytest.mark.asyncio
    async def test_generate_placeholder(self):
        schema = {"voice": "en-US-JennyNeural", "language": "en-US", "speakers": 1}
        results = await self.generator.generate(schema, 2)
        assert len(results) == 2
        assert "transcript" in results[0]
        assert "audio_url" in results[0]
