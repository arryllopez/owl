"""
Owl Backend - AI-Powered Speech Accessibility
FastAPI server using Claude API for speech transcription and emergency detection
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from dotenv import load_dotenv

# Import services
from app.services.openai_service import transcribe_and_analyze_audio
from app.services.elevenlabs import text_to_speech
from app.services.twilio import send_emergency_alert

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Owl API",
    description="AI-powered speech interpretation with OpenAI (Whisper + GPT-4)",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Models
# ============================================================================

class TranscriptionResponse(BaseModel):
    transcribed_text: str
    is_emergency: bool
    emergency_confidence: float
    intent: str
    suggested_response: str
    audio_url: Optional[str] = None  # URL to generated voice response

class EmergencyAlert(BaseModel):
    message: str
    location: Optional[str] = None
    contact_number: str

# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "Owl API v2.0 - Powered by OpenAI",
        "status": "healthy",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "openai": os.getenv("OPENAI_API_KEY") is not None,
            "elevenlabs": os.getenv("ELEVENLABS_API_KEY") is not None,
            "twilio": os.getenv("TWILIO_ACCOUNT_SID") is not None
        }
    }

# ============================================================================
# Main Processing Endpoint
# ============================================================================

@app.post("/api/process-speech", response_model=TranscriptionResponse)
async def process_speech(file: UploadFile = File(...)):
    """
    Main endpoint: Process speech with OpenAI

    Flow:
    1. Receive audio file from user
    2. Whisper transcribes audio → text
    3. GPT-4 analyzes text + detects emergency
    4. If EMERGENCY detected:
       - Send alert via Twilio
       - Return transcription + emergency flag
    5. If NOT emergency:
       - Generate voice response with ElevenLabs
       - Return transcription + audio response
    """
    temp_audio_path = None
    temp_response_path = None

    try:
        # Save uploaded audio to temp file
        temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        with open(temp_audio_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Step 1: OpenAI analyzes audio (Whisper + GPT-4)
        result = transcribe_and_analyze_audio(temp_audio_path)

        # Step 2: Handle based on emergency status
        if result["is_emergency"] and result["emergency_confidence"] > 0.7:
            # EMERGENCY: Send alert via Twilio
            emergency_contact = os.getenv("EMERGENCY_CONTACT_NUMBER")
            if emergency_contact:
                send_emergency_alert(
                    message=result["transcribed_text"],
                    contact_number=emergency_contact,
                    location=None  # TODO: Get from app if available
                )

            return TranscriptionResponse(
                transcribed_text=result["transcribed_text"],
                is_emergency=True,
                emergency_confidence=result["emergency_confidence"],
                intent=result["intent"],
                suggested_response="Emergency services have been notified.",
                audio_url=None
            )

        else:
            # NOT EMERGENCY: Generate voice response
            voice_audio = text_to_speech(
                text=result["suggested_response"],
                voice_id=os.getenv("ELEVENLABS_VOICE_ID")
            )

            if voice_audio:
                # Save voice response
                temp_response_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                with open(temp_response_path, "wb") as f:
                    f.write(voice_audio)

                # TODO: Upload to storage and get permanent URL
                audio_url = f"/api/audio/{os.path.basename(temp_response_path)}"
            else:
                audio_url = None

            return TranscriptionResponse(
                transcribed_text=result["transcribed_text"],
                is_emergency=False,
                emergency_confidence=result["emergency_confidence"],
                intent=result["intent"],
                suggested_response=result["suggested_response"],
                audio_url=audio_url
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    finally:
        # Cleanup temp files
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.unlink(temp_audio_path)
            except:
                pass

# ============================================================================
# Audio Playback
# ============================================================================

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """
    Serve generated audio responses
    """
    temp_dir = tempfile.gettempdir()
    audio_path = os.path.join(temp_dir, filename)

    if os.path.exists(audio_path):
        return FileResponse(audio_path, media_type="audio/mpeg")
    else:
        raise HTTPException(status_code=404, detail="Audio file not found")

# ============================================================================
# Manual Emergency Trigger (for testing)
# ============================================================================

@app.post("/api/emergency")
async def trigger_emergency(alert: EmergencyAlert):
    """
    Manually trigger emergency alert (for testing)
    """
    try:
        send_emergency_alert(
            message=alert.message,
            contact_number=alert.contact_number,
            location=alert.location
        )
        return {
            "status": "success",
            "message": "Emergency alert sent",
            "alert_sent_to": alert.contact_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency alert failed: {str(e)}")

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
