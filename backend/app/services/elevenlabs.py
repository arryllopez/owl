"""
ElevenLabs Service - Voice generation
"""

import os
from elevenlabs.client import ElevenLabs
from typing import Optional

# Client will be initialized lazily
_client: Optional[ElevenLabs] = None

def _get_client() -> ElevenLabs:
    """Get or create ElevenLabs client (lazy initialization)"""
    global _client
    if _client is None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        _client = ElevenLabs(api_key=api_key)
    return _client


def text_to_speech(text: str, voice_id: Optional[str] = None) -> bytes:
    """
    Convert text to speech using ElevenLabs

    Args:
        text: Text to convert to speech
        voice_id: Optional voice ID (uses default if not provided)

    Returns:
        Audio bytes (MP3 format)
    """
    client = _get_client()

    try:
        # Use default voice if none provided
        if not voice_id:
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice (default)

        # Generate audio using ElevenLabs API
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_monolingual_v1"
        )

        # Convert generator to bytes
        audio_bytes = b"".join(audio)
        return audio_bytes

    except Exception as e:
        print(f"ElevenLabs TTS failed: {e}")
        return None


def clone_voice(audio_samples: list, voice_name: str, description: str = "") -> str:
    """
    Clone a voice from audio samples

    Args:
        audio_samples: List of audio file paths
        voice_name: Name for the cloned voice
        description: Description of the voice

    Returns:
        voice_id of cloned voice
    """
    # TODO: Implement voice cloning
    # This requires the ElevenLabs Pro plan
    pass
