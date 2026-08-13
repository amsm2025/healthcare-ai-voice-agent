from uuid import uuid4

from app.models.booking import BookingRequest, BookingResponse


class CalComService:
    """Scheduling integration boundary.

    The default implementation returns a demo booking so the repository runs
    without external credentials. Replace this method with a real Cal.com API
    call after configuring your event type and API credentials.
    """

    async def create_booking(self, request: BookingRequest) -> BookingResponse:
        return BookingResponse(
            booking_id=f"demo-{uuid4().hex[:10]}",
            status="confirmed-demo",
            start_time=request.start_time,
        )