from fastapi import APIRouter

from app.models.booking import BookingRequest, BookingResponse
from app.services.calcom_service import CalComService

router = APIRouter(prefix="/api/v1", tags=["bookings"])
service = CalComService()


@router.post("/bookings", response_model=BookingResponse)
async def create_booking(request: BookingRequest) -> BookingResponse:
    return await service.create_booking(request)
