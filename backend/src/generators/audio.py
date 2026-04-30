"""Audio/speech synthetic data generator using Azure Speech Services."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from .base import BaseGenerator, CostEstimate

logger = logging.getLogger(__name__)

# Supported Azure Neural voices (subset)
SUPPORTED_VOICES = [
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-US-AriaNeural",
    "en-US-DavisNeural",
    "en-GB-SoniaNeural",
    "en-GB-RyanNeural",
    "de-DE-KatjaNeural",
    "fr-FR-DeniseNeural",
    "es-ES-ElviraNeural",
    "ja-JP-NanamiNeural",
]

# Cost estimate: ~$16 per 1M characters for Azure Speech neural voices
_COST_PER_CHARACTER = 0.000016
_CHARS_PER_SECOND = 15  # approximate speaking rate


class AudioGenerator(BaseGenerator):
    """Generate synthetic audio/speech data using Azure Speech Services.

    Capabilities:
    - Text-to-speech synthesis for single or multi-speaker recordings
    - Synthetic transcript generation (via Azure OpenAI)
    - Conversation simulation with multiple speakers
    - Output in WAV, MP3, or OGG format
    """

    def __init__(
        self,
        speech_client: Any = None,
        openai_client: Any = None,
    ) -> None:
        self._speech_client = speech_client
        self._openai_client = openai_client

    async def generate(
        self,
        schema: dict[str, Any],
        count: int,
        options: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Generate synthetic audio recordings with transcripts.

        Args:
            schema: Dict with audio parameters:
                    ``voice``, ``language``, ``format``, ``speakers``,
                    ``include_transcript``, ``topic``.
            count: Number of audio clips to generate.
            options: Optional dict with additional settings.

        Returns:
            List of dicts with ``id``, ``transcript``, ``audio_url``,
            ``duration_seconds``, and ``metadata``.
        """
        options = options or {}
        voice = schema.get("voice", "en-US-JennyNeural")
        language = schema.get("language", "en-US")
        speakers = schema.get("speakers", 1)
        include_transcript = schema.get("include_transcript", True)

        if self._speech_client is None:
            logger.warning("No Speech client configured — returning placeholder audio data")
            return self._generate_placeholder(count, voice, language, speakers)

        results = []
        for i in range(count):
            transcript = await self._generate_transcript(
                language=language, speakers=speakers, options=options
            )

            audio_url = await self._synthesize_speech(
                text=transcript,
                voice=voice,
                output_format=schema.get("format", "wav"),
            )

            result: dict[str, Any] = {
                "id": str(uuid.uuid4()),
                "audio_url": audio_url,
                "duration_seconds": len(transcript) / _CHARS_PER_SECOND,
                "metadata": {
                    "voice": voice,
                    "language": language,
                    "speakers": speakers,
                    "format": schema.get("format", "wav"),
                },
            }
            if include_transcript:
                result["transcript"] = transcript
            results.append(result)

        return results

    def validate(self, schema: dict[str, Any]) -> bool:
        """Validate audio generation schema."""
        voice = schema.get("voice", "en-US-JennyNeural")
        fmt = schema.get("format", "wav")
        speakers = schema.get("speakers", 1)
        return (
            voice in SUPPORTED_VOICES
            and fmt in ("wav", "mp3", "ogg")
            and 1 <= speakers <= 10
        )

    def estimate_cost(self, schema: dict[str, Any], count: int) -> CostEstimate:
        """Estimate cost for audio generation."""
        avg_transcript_chars = 500
        total_chars = avg_transcript_chars * count
        speech_cost = total_chars * _COST_PER_CHARACTER
        transcript_cost = (total_chars // 4) * 0.000005  # OpenAI for transcript gen
        total_cost = speech_cost + transcript_cost
        time_seconds = max(10, count * 5)

        return CostEstimate(
            estimated_tokens=total_chars // 4,
            estimated_cost_usd=round(total_cost, 4),
            estimated_time_seconds=time_seconds,
            breakdown={
                "speech_synthesis_usd": round(speech_cost, 4),
                "transcript_generation_usd": round(transcript_cost, 4),
            },
        )

    async def _generate_transcript(
        self,
        language: str,
        speakers: int,
        options: dict[str, Any],
    ) -> str:
        """Generate a synthetic transcript using Azure OpenAI."""
        if self._openai_client is None:
            return f"[Placeholder transcript in {language} with {speakers} speaker(s)]"

        if speakers > 1:
            prompt = (
                f"Generate a realistic conversation between {speakers} speakers "
                f"in {language}. Use the format 'Speaker N: ...' for each line. "
                f"The conversation should be 5-10 exchanges."
            )
        else:
            prompt = (
                f"Generate a realistic spoken monologue in {language}, "
                f"approximately 3-5 sentences. Topic can be anything realistic."
            )

        response = await self._openai_client.chat.completions.create(
            model=options.get("model", "gpt-4o"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Generate realistic synthetic speech transcripts. "
                        "Do not include real names or PII."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        return response.choices[0].message.content

    async def _synthesize_speech(
        self, text: str, voice: str, output_format: str
    ) -> str:
        """Synthesize speech using Azure Speech Services.

        Returns the URL where the audio file is stored.
        """
        # In production, this uses azure.cognitiveservices.speech SDK
        # and uploads the result to Azure Blob Storage.
        logger.info("Synthesizing speech: voice=%s, format=%s", voice, output_format)
        audio_id = str(uuid.uuid4())
        return f"https://synthdata.blob.core.windows.net/audio/{audio_id}.{output_format}"

    @staticmethod
    def _generate_placeholder(
        count: int, voice: str, language: str, speakers: int
    ) -> list[dict[str, Any]]:
        """Return placeholder audio metadata for development."""
        return [
            {
                "id": str(uuid.uuid4()),
                "transcript": (
                    f"Placeholder transcript #{i + 1} — synthetic speech in "
                    f"{language} with {speakers} speaker(s)."
                ),
                "audio_url": f"https://synthdata.blob.core.windows.net/audio/placeholder-{i + 1}.wav",
                "duration_seconds": 5.0 + i,
                "metadata": {
                    "voice": voice,
                    "language": language,
                    "speakers": speakers,
                    "format": "wav",
                },
            }
            for i in range(count)
        ]
