import logging
import re

import httpx

from app.core.config import get_settings
from app.services.safety import detect_emergency, emergency_message

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """You are a healthcare appointment scheduling assistant.
Your role is limited to appointment scheduling, clinic navigation, and general administrative guidance.
Do not diagnose conditions, recommend treatment or medication, or request unnecessary sensitive medical information.
Keep responses concise and guide scheduling users toward a preferred date and time.
"""


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def reply(self, message: str) -> tuple[str, str, bool]:
        if detect_emergency(message):
            return emergency_message(), "emergency", False
        intent = self._classify_intent(message)
        if self.settings.llm_mode.lower() == "live" and self.settings.openai_api_key:
            provider_reply = await self._reply_with_openai(message)
            if provider_reply:
                return provider_reply, intent, True
        return self._fallback_reply(intent), intent, True

    async def _reply_with_openai(self, message: str) -> str | None:
        payload = {"model": self.settings.openai_model, "instructions": SYSTEM_INSTRUCTIONS, "input": message, "store": False}
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.settings.openai_timeout_seconds) as client:
                response = await client.post(f"{self.settings.openai_base_url.rstrip('/')}/responses", headers=headers, json=payload)
                response.raise_for_status()
            return self._extract_output_text(response.json())
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            logger.warning("LLM provider request failed; using fallback: %s", exc)
            return None

    @staticmethod
    def _extract_output_text(data: dict) -> str | None:
        for output_item in data.get("output", []):
            if output_item.get("type") != "message":
                continue
            for content_item in output_item.get("content", []):
                if content_item.get("type") == "output_text":
                    text = content_item.get("text", "").strip()
                    if text:
                        return text
        return None

    @staticmethod
    def _classify_intent(message: str) -> str:
        lowered = message.lower().strip()
        if re.search(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", lowered):
            return "contact_details"
        schedule_details = (
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "tomorrow", "morning", "afternoon", "evening", "noon",
        )
        if any(term in lowered for term in schedule_details) or re.search(r"\b\d{1,2}(:\d{2})?\s*(a\.?m\.?|p\.?m\.?)\b", lowered):
            return "appointment_time"
        if any(term in lowered for term in ("book", "schedule", "appointment", "consultation")):
            return "schedule_appointment"
        if any(term in lowered for term in ("hello", "hi", "hey", "hola", "good morning", "good afternoon", "good evening")):
            return "greeting"
        return "general"

    @staticmethod
    def _fallback_reply(intent: str) -> str:
        replies = {
            "greeting": "Hello! I can help you arrange a clinic appointment. Would you like to choose a preferred date and time?",
            "schedule_appointment": "Certainly. What day and time would you prefer for your appointment?",
            "appointment_time": "Thank you. I noted your preferred schedule. Please provide your name and email address in one message so I can prepare the appointment request.",
            "contact_details": "Thank you. Your appointment request details have been captured for this demonstration. A production version would now confirm availability and create the booking through the scheduling provider.",
            "general": "I can help with appointment scheduling and general clinic navigation. I cannot diagnose conditions or recommend treatment. Would you like to schedule an appointment?",
        }
        return replies[intent]
