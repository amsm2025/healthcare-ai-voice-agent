import logging

import httpx

from app.core.config import get_settings
from app.services.safety import detect_emergency, emergency_message

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTIONS = """You are a healthcare appointment scheduling assistant.

Your role is limited to:
- appointment scheduling;
- clinic navigation;
- general administrative guidance.

You must not:
- diagnose medical conditions;
- recommend treatment or medication;
- ask for unnecessary sensitive medical information.

Keep responses concise. If the user wants to schedule or book an appointment,
guide them toward choosing a preferred date and time.
"""


class LLMService:
    """Provider-backed LLM service with a deterministic demo fallback.

    Demo mode is the default so tests and local development do not require
    network access or API credentials.

    Set LLM_MODE=live and provide OPENAI_API_KEY to use the OpenAI Responses API.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    async def reply(self, message: str) -> tuple[str, str, bool]:
        # Safety checks always happen before any model/provider call.
        if detect_emergency(message):
            return emergency_message(), "emergency", False

        intent = self._classify_intent(message)

        if (
            self.settings.llm_mode.lower() == "live"
            and self.settings.openai_api_key
        ):
            provider_reply = await self._reply_with_openai(message)
            if provider_reply:
                return provider_reply, intent, True

        return self._fallback_reply(intent), intent, True

    async def _reply_with_openai(self, message: str) -> str | None:
        payload = {
            "model": self.settings.openai_model,
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": message,
            # Explicitly disable response storage for this demo integration.
            "store": False,
        }

        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.openai_timeout_seconds
            ) as client:
                response = await client.post(
                    f"{self.settings.openai_base_url.rstrip('/')}/responses",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

            return self._extract_output_text(response.json())

        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            # Do not expose provider errors or credentials to the end user.
            logger.warning("LLM provider request failed; using fallback: %s", exc)
            return None

    @staticmethod
    def _extract_output_text(data: dict) -> str | None:
        """Extract text from a Responses API response without SDK coupling."""
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
        lowered = message.lower()
        scheduling_terms = ("book", "schedule", "appointment", "consultation")

        if any(term in lowered for term in scheduling_terms):
            return "schedule_appointment"

        return "general"

    @staticmethod
    def _fallback_reply(intent: str) -> str:
        if intent == "schedule_appointment":
            return (
                "I can help you schedule an appointment. "
                "Please choose a preferred date and time in the booking form. "
                "For privacy, avoid entering detailed medical information."
            )

        return (
            "I can help with appointment scheduling and general clinic navigation. "
            "I cannot diagnose conditions or recommend treatment. "
            "Would you like to schedule an appointment?"
        )
