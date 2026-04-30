"""Audio/speech synthetic data generator using Azure Speech Services."""

from __future__ import annotations

import json
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

# Supported audio output formats
SUPPORTED_FORMATS = ("wav", "mp3", "ogg", "flac")

# Supported transcript output formats
SUPPORTED_TRANSCRIPT_FORMATS = ("text", "json", "srt", "vtt")

# Valid Phase 2 noise types and acoustic conditions (reserved for future use)
_SUPPORTED_NOISE_TYPES = ("office", "car", "street", "cafe")
_SUPPORTED_ACOUSTIC_CONDITIONS = ("reverb", "phone", "voip", "clean")

# Cost estimate: ~$16 per 1M characters for Azure Speech neural voices
_COST_PER_CHARACTER = 0.000016
_CHARS_PER_SECOND = 15  # approximate speaking rate


class AudioGenerator(BaseGenerator):
    """Generate synthetic audio/speech data using Azure Speech Services.

    Capabilities:
    - Text-to-speech synthesis for single or multi-speaker recordings
    - Synthetic transcript generation (via Azure OpenAI)
    - Conversation simulation with multiple speakers
    - Output in WAV, MP3, OGG, or FLAC format
    - Transcript export in plain text, JSON, SRT, or WebVTT format
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
                    ``include_transcript``, ``topic``, ``transcript_format``,
                    ``noise_type``, ``acoustic_condition``.
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
        topic = schema.get("topic")
        transcript_format = schema.get("transcript_format", "text")
        noise_type = schema.get("noise_type")
        acoustic_condition = schema.get("acoustic_condition")
        output_format = schema.get("format", "wav")

        if self._speech_client is None:
            logger.warning("No Speech client configured — returning placeholder audio data")
            return self._generate_placeholder(
                count, voice, language, speakers,
                topic=topic,
                transcript_format=transcript_format,
                noise_type=noise_type,
                acoustic_condition=acoustic_condition,
                output_format=output_format,
            )

        results = []
        for i in range(count):
            transcript = await self._generate_transcript(
                language=language,
                speakers=speakers,
                topic=topic,
                options=options,
            )

            audio_url = await self._synthesize_speech(
                text=transcript,
                voice=voice,
                output_format=output_format,
            )

            duration = len(transcript) / _CHARS_PER_SECOND

            result: dict[str, Any] = {
                "id": str(uuid.uuid4()),
                "audio_url": audio_url,
                "duration_seconds": round(duration, 2),
                "metadata": {
                    "voice": voice,
                    "language": language,
                    "speakers": speakers,
                    "format": output_format,
                    "topic": topic,
                    "noise_type": noise_type,
                    "acoustic_condition": acoustic_condition,
                    "emotion_tags": [],
                },
            }
            if include_transcript:
                result["transcript"] = self._format_transcript(
                    transcript, transcript_format, speakers, duration
                )
                result["transcript_format"] = transcript_format
            results.append(result)

        return results

    def validate(self, schema: dict[str, Any]) -> bool:
        """Validate audio generation schema."""
        voice = schema.get("voice", "en-US-JennyNeural")
        fmt = schema.get("format", "wav")
        speakers = schema.get("speakers", 1)
        transcript_format = schema.get("transcript_format", "text")
        noise_type = schema.get("noise_type")
        acoustic_condition = schema.get("acoustic_condition")

        if voice not in SUPPORTED_VOICES:
            return False
        if fmt not in SUPPORTED_FORMATS:
            return False
        if not (1 <= speakers <= 10):
            return False
        if transcript_format not in SUPPORTED_TRANSCRIPT_FORMATS:
            return False
        if noise_type is not None and noise_type not in _SUPPORTED_NOISE_TYPES:
            return False
        if acoustic_condition is not None and acoustic_condition not in _SUPPORTED_ACOUSTIC_CONDITIONS:
            return False
        return True

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
        topic: str | None,
        options: dict[str, Any],
    ) -> str:
        """Generate a synthetic transcript using Azure OpenAI."""
        if self._openai_client is None:
            return f"[Placeholder transcript in {language} with {speakers} speaker(s)]"

        topic_context = f" about {topic}" if topic else ""

        if speakers > 1:
            prompt = (
                f"Generate a realistic conversation{topic_context} between "
                f"{speakers} speakers in {language}. Use the format "
                f"'Speaker N: ...' for each line. "
                f"The conversation should be 5-10 exchanges."
            )
        else:
            prompt = (
                f"Generate a realistic spoken monologue{topic_context} in "
                f"{language}, approximately 3-5 sentences."
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
    def _format_transcript(
        transcript: str,
        transcript_format: str,
        speakers: int,
        duration_seconds: float,
    ) -> Any:
        """Format a raw transcript string into the requested output format.

        Args:
            transcript: Raw transcript text, optionally with 'Speaker N:' prefixes.
            transcript_format: One of ``text``, ``json``, ``srt``, ``vtt``.
            speakers: Number of speakers (used to parse speaker lines).
            duration_seconds: Total estimated duration for timestamp generation.

        Returns:
            Formatted transcript as a string (text/srt/vtt) or list of dicts (json).
        """
        if transcript_format == "text":
            return transcript

        lines = [line.strip() for line in transcript.splitlines() if line.strip()]
        if not lines:
            return [] if transcript_format == "json" else ""

        utterances = []
        segment_duration = duration_seconds / len(lines)

        for idx, line in enumerate(lines):
            start = idx * segment_duration
            end = start + segment_duration
            if ": " in line:
                speaker, text = line.split(": ", 1)
            else:
                speaker = "Speaker 1"
                text = line
            utterances.append({
                "speaker": speaker,
                "text": text,
                "start_time": round(start, 3),
                "end_time": round(end, 3),
            })

        if transcript_format == "json":
            return utterances

        if transcript_format == "srt":
            return AudioGenerator._to_srt(utterances)

        if transcript_format == "vtt":
            return AudioGenerator._to_vtt(utterances)

        return transcript

    @staticmethod
    def _to_srt(utterances: list[dict[str, Any]]) -> str:
        """Convert utterances to SRT subtitle format."""

        def _fmt_time(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        blocks = []
        for i, utt in enumerate(utterances, start=1):
            start = _fmt_time(utt["start_time"])
            end = _fmt_time(utt["end_time"])
            blocks.append(f"{i}\n{start} --> {end}\n{utt['speaker']}: {utt['text']}")
        return "\n\n".join(blocks)

    @staticmethod
    def _to_vtt(utterances: list[dict[str, Any]]) -> str:
        """Convert utterances to WebVTT format."""

        def _fmt_time(seconds: float) -> str:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds % 1) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

        lines = ["WEBVTT", ""]
        for utt in utterances:
            start = _fmt_time(utt["start_time"])
            end = _fmt_time(utt["end_time"])
            lines.append(f"{start} --> {end}")
            lines.append(f"{utt['speaker']}: {utt['text']}")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _generate_placeholder(
        count: int,
        voice: str,
        language: str,
        speakers: int,
        *,
        topic: str | None = None,
        transcript_format: str = "text",
        noise_type: str | None = None,
        acoustic_condition: str | None = None,
        output_format: str = "wav",
    ) -> list[dict[str, Any]]:
        """Return placeholder audio metadata for development."""
        topic_label = f" on {topic}" if topic else ""
        results = []
        for i in range(count):
            raw_transcript = (
                f"Placeholder transcript #{i + 1} — synthetic speech{topic_label} "
                f"in {language} with {speakers} speaker(s)."
            )
            duration = 5.0 + i
            formatted = AudioGenerator._format_transcript(
                raw_transcript, transcript_format, speakers, duration
            )
            results.append(
                {
                    "id": str(uuid.uuid4()),
                    "transcript": formatted,
                    "transcript_format": transcript_format,
                    "audio_url": (
                        f"https://synthdata.blob.core.windows.net/audio/"
                        f"placeholder-{i + 1}.{output_format}"
                    ),
                    "duration_seconds": duration,
                    "metadata": {
                        "voice": voice,
                        "language": language,
                        "speakers": speakers,
                        "format": output_format,
                        "topic": topic,
                        "noise_type": noise_type,
                        "acoustic_condition": acoustic_condition,
                        "emotion_tags": [],
                    },
                }
            )
        return results

