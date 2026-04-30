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

    def test_validate_flac_format(self):
        schema = {"voice": "en-US-JennyNeural", "format": "flac", "speakers": 1}
        assert self.generator.validate(schema) is True

    def test_validate_invalid_transcript_format(self):
        schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 1, "transcript_format": "xml"}
        assert self.generator.validate(schema) is False

    def test_validate_valid_transcript_formats(self):
        for fmt in ("text", "json", "srt", "vtt"):
            schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 1, "transcript_format": fmt}
            assert self.generator.validate(schema) is True, f"Expected valid for transcript_format={fmt}"

    def test_validate_invalid_noise_type(self):
        schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 1, "noise_type": "underwater"}
        assert self.generator.validate(schema) is False

    def test_validate_valid_noise_type(self):
        schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 1, "noise_type": "office"}
        assert self.generator.validate(schema) is True

    def test_validate_invalid_acoustic_condition(self):
        schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 1, "acoustic_condition": "tunnel"}
        assert self.generator.validate(schema) is False

    def test_validate_valid_acoustic_condition(self):
        schema = {"voice": "en-US-JennyNeural", "format": "wav", "speakers": 1, "acoustic_condition": "reverb"}
        assert self.generator.validate(schema) is True

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

    @pytest.mark.asyncio
    async def test_generate_with_topic(self):
        schema = {
            "voice": "en-US-JennyNeural",
            "language": "en-US",
            "speakers": 1,
            "topic": "customer support",
        }
        results = await self.generator.generate(schema, 1)
        assert len(results) == 1
        assert results[0]["metadata"]["topic"] == "customer support"

    @pytest.mark.asyncio
    async def test_generate_flac_format(self):
        schema = {"voice": "en-US-JennyNeural", "language": "en-US", "format": "flac"}
        results = await self.generator.generate(schema, 1)
        assert results[0]["audio_url"].endswith(".flac")
        assert results[0]["metadata"]["format"] == "flac"

    @pytest.mark.asyncio
    async def test_generate_transcript_format_srt(self):
        schema = {
            "voice": "en-US-JennyNeural",
            "language": "en-US",
            "speakers": 1,
            "transcript_format": "srt",
        }
        results = await self.generator.generate(schema, 1)
        assert results[0]["transcript_format"] == "srt"
        assert "-->" in results[0]["transcript"]

    @pytest.mark.asyncio
    async def test_generate_transcript_format_vtt(self):
        schema = {
            "voice": "en-US-JennyNeural",
            "language": "en-US",
            "speakers": 1,
            "transcript_format": "vtt",
        }
        results = await self.generator.generate(schema, 1)
        assert results[0]["transcript_format"] == "vtt"
        assert results[0]["transcript"].startswith("WEBVTT")

    @pytest.mark.asyncio
    async def test_generate_transcript_format_json(self):
        schema = {
            "voice": "en-US-JennyNeural",
            "language": "en-US",
            "speakers": 1,
            "transcript_format": "json",
        }
        results = await self.generator.generate(schema, 1)
        assert results[0]["transcript_format"] == "json"
        assert isinstance(results[0]["transcript"], list)
        assert len(results[0]["transcript"]) > 0
        utterance = results[0]["transcript"][0]
        assert "speaker" in utterance
        assert "text" in utterance
        assert "start_time" in utterance
        assert "end_time" in utterance

    @pytest.mark.asyncio
    async def test_generate_metadata_emotion_tags(self):
        schema = {"voice": "en-US-JennyNeural", "language": "en-US"}
        results = await self.generator.generate(schema, 1)
        assert "emotion_tags" in results[0]["metadata"]
        assert isinstance(results[0]["metadata"]["emotion_tags"], list)

    @pytest.mark.asyncio
    async def test_generate_noise_type_in_metadata(self):
        schema = {
            "voice": "en-US-JennyNeural",
            "language": "en-US",
            "noise_type": "office",
            "acoustic_condition": "reverb",
        }
        results = await self.generator.generate(schema, 1)
        assert results[0]["metadata"]["noise_type"] == "office"
        assert results[0]["metadata"]["acoustic_condition"] == "reverb"

    def test_format_transcript_text(self):
        raw = "Speaker 1: Hello.\nSpeaker 2: Hi there."
        result = AudioGenerator._format_transcript(raw, "text", 2, 10.0)
        assert result == raw

    def test_format_transcript_json(self):
        raw = "Speaker 1: Hello.\nSpeaker 2: Hi there."
        result = AudioGenerator._format_transcript(raw, "json", 2, 10.0)
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["speaker"] == "Speaker 1"
        assert result[0]["text"] == "Hello."

    def test_format_transcript_srt(self):
        raw = "Speaker 1: Hello.\nSpeaker 2: Hi there."
        result = AudioGenerator._format_transcript(raw, "srt", 2, 10.0)
        assert "00:00:00,000 --> 00:00:05,000" in result
        assert "Speaker 1: Hello." in result

    def test_format_transcript_vtt(self):
        raw = "Speaker 1: Hello.\nSpeaker 2: Hi there."
        result = AudioGenerator._format_transcript(raw, "vtt", 2, 10.0)
        assert result.startswith("WEBVTT")
        assert "00:00:00.000 --> 00:00:05.000" in result
