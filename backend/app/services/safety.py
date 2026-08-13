EMERGENCY_TERMS = {
    "chest pain",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "suicidal",
    "suicide",
    "unconscious",
    "stroke",
    "heart attack",
}


def detect_emergency(text: str) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in EMERGENCY_TERMS)


def emergency_message() -> str:
    return (
        "Your message may describe an urgent medical situation. "
        "This scheduling assistant cannot provide emergency care or medical advice. "
        "Please contact your local emergency service or go to the nearest emergency department now."
    )
