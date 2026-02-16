"""
Owl Backend - AI-Powered Speech Accessibility
FastAPI server for speech transcription, voice cloning, and emergency detection
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Owl API",
    description="AI-powered speech interpretation and emergency detection system",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Models
# ============================================================================

class TranscriptionResponse(BaseModel):
    text: str
    confidence: float
    language: str
    alternatives: List[dict]
    is_emergency: bool

class SpeakRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    language: Optional[str] = "en"

class EmergencyAlert(BaseModel):
    message: str
    location: Optional[str] = None
    contact_number: str

class VoiceCloneRequest(BaseModel):
    name: str
    description: Optional[str] = None

# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "Owl API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "whisper": os.getenv("OPENAI_API_KEY") is not None,
            "elevenlabs": os.getenv("ELEVENLABS_API_KEY") is not None,
            "twilio": os.getenv("TWILIO_ACCOUNT_SID") is not None
        }
    }

# ============================================================================
# Speech Recognition
# ============================================================================

@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file using fine-tuned Whisper ASR

    Fine-tuned Whisper outputs clean transcription directly from unclear speech.
    No post-processing/corrections needed - the model handles dysarthric speech.

    Flow:
    1. Receive audio file (unclear speech)
    2. Fine-tuned Whisper transcribes → clean text
    3. Detect emergency phrases
    4. Return transcription + emergency flag
    """
    try:
        # TODO: Implement fine-tuned Whisper transcription
        # 1. Save uploaded audio file temporarily
        # 2. Load fine-tuned Whisper model
        # 3. Transcribe audio → clean text
        # 4. Extract confidence scores and alternatives from beam search
        # 5. Detect emergency

        # Mock response for now
        transcribed_text = "I want coffee, hot"  # Fine-tuned model output
        confidence = 0.87
        language = "en"

        # Alternatives from beam search (top 3 hypotheses)
        alternatives = [
            {"text": "I want coffee, hot", "confidence": 0.87},
            {"text": "I want coffee cold", "confidence": 0.65},
            {"text": "I need coffee now", "confidence": 0.58}
        ]

        # Check for emergency
        is_emergency = detect_emergency(transcribed_text, confidence)

        return TranscriptionResponse(
            text=transcribed_text,
            confidence=confidence,
            language=language,
            alternatives=alternatives,
            is_emergency=is_emergency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

# ============================================================================
# Text-to-Speech (Voice Cloning)
# ============================================================================

@app.post("/api/speak")
async def text_to_speech(request: SpeakRequest):
    """
    Convert text to speech using ElevenLabs voice cloning
    Returns audio file in user's cloned voice
    """
    try:
        # TODO: Implement ElevenLabs TTS
        return {
            "status": "success",
            "message": "TTS generation not yet implemented",
            "text": request.text,
            "voice_id": request.voice_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.post("/api/voice/clone")
async def clone_voice(files: List[UploadFile] = File(...)):
    """
    Create voice clone from uploaded audio samples
    Requires 20-30 seconds of clear audio
    """
    try:
        # TODO: Implement ElevenLabs voice cloning
        return {
            "status": "success",
            "message": "Voice cloning not yet implemented",
            "samples_received": len(files)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")

# ============================================================================
# Emergency Detection & Calling
# ============================================================================

@app.post("/api/emergency")
async def trigger_emergency(alert: EmergencyAlert):
    """
    Send emergency alert via Twilio SMS/Call
    """
    try:
        # TODO: Implement Twilio emergency calling
        return {
            "status": "success",
            "message": "Emergency alert not yet implemented",
            "alert_sent_to": alert.contact_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency alert failed: {str(e)}")

# ============================================================================
# Emergency Detection
# ============================================================================

def detect_emergency(text: str, confidence: float) -> bool:
    """
    Detect emergency phrases in transcription

    Since fine-tuned Whisper outputs clean text, we can reliably
    detect emergency phrases without fuzzy matching.

    Args:
        text: Clean transcription from fine-tuned Whisper
        confidence: Transcription confidence score

    Returns:
        True if emergency detected with >90% confidence
    """
    # Only trigger emergency if confidence is high enough
    if confidence < 0.90:
        return False

    # Emergency phrases (English + Spanish)
    emergency_phrases = [
        # English
        "help", "emergency", "call for help", "need help",
        "ambulance", "fell down", "can't breathe", "call 911",
        "help me", "call ambulance", "need doctor",

        # Spanish
        "ayuda", "urgencia", "emergencia", "llamar ambulancia"
    ]

    text_lower = text.lower()
    for phrase in emergency_phrases:
        if phrase in text_lower:
            return True

    return False

# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
