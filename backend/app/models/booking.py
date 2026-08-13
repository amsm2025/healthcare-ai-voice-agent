from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class BookingRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    start_time: datetime
    reason: str = Field(default="General consultation", max_length=500)


class BookingResponse(BaseModel):
    booking_id: str
    status: str
    start_time: datetime
