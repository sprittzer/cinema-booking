from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .models import BookingStatus


class SeatInfo(BaseModel):
    id: int
    row: int
    number: int
    seat_type: str
    price: float


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    session_id: int
    status: BookingStatus
    ticket_code: str | None
    total_price: float


class BookingDetailResponse(BookingResponse):
    movie_title: str
    start_time: datetime
    hall_name: str
    seats: list[SeatInfo]


class CreateBookingRequest(BaseModel):
    session_id: int
    seat_ids: list[int]


class PayBookingResponse(BookingResponse):
    qr_code: str


class ScanTicketRequest(BaseModel):
    ticket_code: str


class ScanTicketResponse(BaseModel):
    booking_id: int
    movie_title: str
    start_time: datetime
    hall_name: str
    seats: list[SeatInfo]
    user_name: str
