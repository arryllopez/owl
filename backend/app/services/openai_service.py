"""
OpenAI Service - Audio transcription (Whisper) + Emergency detection (GPT-4)
Single provider for all AI functionality
"""

import os
from openai import OpenAI
from typing import Dict, Optional
import json

# Client will be initialized lazily
_client: Optional[OpenAI] = None

def _get_client() -> OpenAI:
    """Get or create OpenAI client (lazy initialization)"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _client = OpenAI(api_key=api_key)
    return _client


def transcribe_and_analyze_audio(audio_file_path: str) -> Dict:
    """
    Use OpenAI to transcribe audio and detect emergency situations

    Two-step process:
    1. Whisper transcribes audio → text
    2. GPT-4 analyzes text for emergencies + generates response

    Args:
        audio_file_path: Path to audio file

    Returns:
        dict with:
        - transcribed_text: Clean transcription
        - is_emergency: Boolean
        - emergency_confidence: 0-1 score
        - intent: What the user is trying to communicate
        - suggested_response: What to say back
    """
    client = _get_client()

    try:
        # Step 1: Transcribe audio with Whisper
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        transcribed_text = transcript.strip()

        # Step 2: Analyze transcription with GPT-4
        analysis_prompt = f"""You are an AI assistant helping people with speech difficulties communicate.

Analyze this transcribed speech:
"{transcribed_text}"

Determine:
1. If this is an EMERGENCY requiring immediate help
2. The person's intent/what they need
3. An appropriate response

EMERGENCY situations include:
- Medical emergencies (chest pain, can't breathe, fell, injury)
- Calls for help
- Requests for ambulance/911
- Dangerous situations

Respond in this EXACT JSON format:
{{
  "is_emergency": true or false,
  "emergency_confidence": 0.0 to 1.0,
  "intent": "what they want/need",
  "suggested_response": "appropriate reply to say back"
}}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant for people with speech difficulties. Always respond with valid JSON."},
                {"role": "user", "content": analysis_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("OpenAI returned empty response")

        analysis = json.loads(content)

        return {
            "transcribed_text": transcribed_text,
            "is_emergency": analysis.get("is_emergency", False),
            "emergency_confidence": analysis.get("emergency_confidence", 0.0),
            "intent": analysis.get("intent", "unknown"),
            "suggested_response": analysis.get("suggested_response", "I'm here to help.")
        }

    except Exception as e:
        print(f"OpenAI processing failed: {e}")
        return {
            "transcribed_text": "",
            "is_emergency": False,
            "emergency_confidence": 0.0,
            "intent": "error",
            "suggested_response": "Sorry, I couldn't understand that.",
            "error": str(e)
        }


def quick_transcribe(audio_file_path: str) -> str:
    """
    Quick transcription without emergency detection
    Useful for non-critical communications
    """
    client = _get_client()

    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript.strip()

    except Exception as e:
        print(f"Whisper transcription failed: {e}")
        return ""
