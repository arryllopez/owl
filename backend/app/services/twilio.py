"""
Twilio Service - Emergency alerts via SMS/Call
"""

import os
from twilio.rest import Client
from typing import Optional

# Initialize Twilio client
client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)


def send_emergency_alert(
    message: str,
    contact_number: str,
    location: Optional[str] = None
) -> bool:
    """
    Send emergency alert via SMS

    Args:
        message: Emergency message to send
        contact_number: Phone number to alert
        location: Optional location information

    Returns:
        True if sent successfully
    """
    try:
        # Format emergency message
        alert_message = f"🚨 EMERGENCY ALERT 🚨\n\n"
        alert_message += f"Message: {message}\n"

        if location:
            alert_message += f"Location: {location}\n"

        alert_message += f"\nThis is an automated alert from Owl."

        # Send SMS
        sms = client.messages.create(
            body=alert_message,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=contact_number
        )

        print(f"Emergency alert sent: {sms.sid}")
        return True

    except Exception as e:
        print(f"Failed to send emergency alert: {e}")
        return False


def make_emergency_call(
    contact_number: str,
    message: str,
    location: Optional[str] = None
) -> bool:
    """
    Make an emergency phone call with text-to-speech

    Args:
        contact_number: Phone number to call
        message: Message to speak
        location: Optional location information

    Returns:
        True if call initiated successfully
    """
    try:
        # Create TwiML for the call
        twiml = f"""
        <Response>
            <Say voice="alice">
                This is an emergency alert.
                {message}.
                {f"Location: {location}." if location else ""}
                Please respond immediately.
            </Say>
        </Response>
        """

        # Make call
        call = client.calls.create(
            twiml=twiml,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=contact_number
        )

        print(f"Emergency call initiated: {call.sid}")
        return True

    except Exception as e:
        print(f"Failed to make emergency call: {e}")
        return False
