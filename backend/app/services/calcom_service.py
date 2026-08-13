import logging
from datetime import timezone
from uuid import uuid4

import httpx

from app.core.config import get_settings
from app.models.booking import BookingRequest, BookingResponse

logger = logging.getLogger(__name__)


class CalComIntegrationError(RuntimeError):
    """Raised when live Cal.com booking creation fails."""


class CalComService:
    """Cal.com booking integration with an explicit demo fallback.

    Demo mode keeps local development and CI deterministic.
    Set CALCOM_MODE=live and configure credentials/event type to call Cal.com.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    async def create_booking(self, request: BookingRequest) -> BookingResponse:
        if self.settings.calcom_mode.lower() != "live":
            return self._demo_booking(request)

        if not self.settings.calcom_api_key:
            raise CalComIntegrationError(
                "Cal.com live mode requires CALCOM_API_KEY."
            )

        if not self.settings.calcom_event_type_id:
            raise CalComIntegrationError(
                "Cal.com live mode requires CALCOM_EVENT_TYPE_ID."
            )

        return await self._create_live_booking(request)

    async def _create_live_booking(
        self, request: BookingRequest
    ) -> BookingResponse:
        start_time = request.start_time

        if start_time.tzinfo is None:
            # Treat a timezone-naive input as UTC rather than silently applying
            # a machine-local timezone.
            start_time = start_time.replace(tzinfo=timezone.utc)

        start_utc = start_time.astimezone(timezone.utc)
        start_value = start_utc.isoformat().replace("+00:00", "Z")

        try:
            event_type_id = int(self.settings.calcom_event_type_id)
        except ValueError as exc:
            raise CalComIntegrationError(
                "CALCOM_EVENT_TYPE_ID must be a numeric Cal.com event type ID."
            ) from exc

        payload = {
            "start": start_value,
            "attendee": {
                "name": request.name,
                "email": str(request.email),
                "timeZone": request.timezone,
                "language": request.language,
            },
            "eventTypeId": event_type_id,
            "metadata": {
                "source": "healthcare-ai-voice-agent",
            },
        }

        headers = {
            "Authorization": f"Bearer {self.settings.calcom_api_key}",
            "Content-Type": "application/json",
            "cal-api-version": self.settings.calcom_api_version,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.calcom_timeout_seconds
            ) as client:
                response = await client.post(
                    f"{self.settings.calcom_base_url.rstrip('/')}/v2/bookings",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()

        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Cal.com booking request failed: %s", exc)
            raise CalComIntegrationError(
                "The scheduling provider could not create the booking."
            ) from exc

        data = body.get("data")
        if not isinstance(data, dict):
            raise CalComIntegrationError(
                "The scheduling provider returned an unexpected response."
            )

        booking_id = str(data.get("uid") or data.get("id") or "")
        if not booking_id:
            raise CalComIntegrationError(
                "The scheduling provider response did not include a booking ID."
            )

        status = str(data.get("status") or "accepted")
        returned_start = data.get("start")

        if returned_start:
            parsed_start = request.start_time.__class__.fromisoformat(
                str(returned_start).replace("Z", "+00:00")
            )
        else:
            parsed_start = start_utc

        return BookingResponse(
            booking_id=booking_id,
            status=status,
            start_time=parsed_start,
        )

    @staticmethod
    def _demo_booking(request: BookingRequest) -> BookingResponse:
        return BookingResponse(
            booking_id=f"demo-{uuid4().hex[:10]}",
            status="confirmed-demo",
            start_time=request.start_time,
        )
