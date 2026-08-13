from app.services.safety import detect_emergency, emergency_message


class LLMService:
    \"\"\"Portfolio-safe LLM abstraction.

    Replace the fallback logic with your approved LLM SDK implementation.
    Keeping the provider behind this interface makes testing and replacement easier.
    \"\"\"

    async def reply(self, message: str) -> tuple[str, str, bool]:
        if detect_emergency(message):
            return emergency_message(), "emergency", False

        lowered = message.lower()

        if any(word in lowered for word in ("book", "schedule", "appointment", "consultation")):
            return (
                "I can help you schedule an appointment. "
                "Please choose a preferred date and time in the booking form. "
                "For privacy, avoid entering detailed medical information.",
                "schedule_appointment",
                True,
            )

        return (
            "I can help with appointment scheduling and general clinic navigation. "
            "I cannot diagnose conditions or recommend treatment. "
            "Would you like to schedule an appointment?",
            "general",
            True,
        )
