"""Azure Speech Services integration for SynthData."""

from __future__ import annotations

import logging

from ..config import get_settings

logger = logging.getLogger(__name__)


def get_speech_config():
    """Create an Azure Speech SDK config from environment settings.

    Returns None if credentials are not configured.

    Note: Requires ``azure-cognitiveservices-speech`` package.
    """
    settings = get_settings()

    if not settings.AZURE_SPEECH_KEY:
        logger.warning(
            "Azure Speech not configured — set AZURE_SPEECH_KEY and "
            "AZURE_SPEECH_REGION environment variables"
        )
        return None

    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        logger.error(
            "azure-cognitiveservices-speech package not installed. "
            "Install with: pip install azure-cognitiveservices-speech"
        )
        return None

    return speechsdk.SpeechConfig(
        subscription=settings.AZURE_SPEECH_KEY,
        region=settings.AZURE_SPEECH_REGION,
    )


async def synthesize_to_file(
    text: str,
    voice: str = "en-US-JennyNeural",
    output_path: str = "output.wav",
) -> str:
    """Synthesize speech from text and save to a file.

    Args:
        text: Text to synthesize.
        voice: Azure Neural voice name.
        output_path: Path to write the audio file.

    Returns:
        Path to the generated audio file.
    """
    config = get_speech_config()
    if config is None:
        logger.warning("Speech config not available — skipping synthesis")
        return ""

    import azure.cognitiveservices.speech as speechsdk

    config.speech_synthesis_voice_name = voice
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config, audio_config=audio_config
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        logger.info("Audio synthesized to %s", output_path)
        return output_path
    else:
        logger.error("Speech synthesis failed: %s", result.reason)
        return ""
