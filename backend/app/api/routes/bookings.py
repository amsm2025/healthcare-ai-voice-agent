from fastapi import APIRouter, HTTPException, status

from app.models.booking import BookingRequest, BookingResponse
from app.services.calcom_service import CalComIntegrationError, CalComService

router = APIRouter(prefix="/api/v1", tags=["bookings"])
service = CalComService()


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(request: BookingRequest) -> BookingResponse:
    try:
        return await service.create_booking(request)
    except CalComIntegrationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
