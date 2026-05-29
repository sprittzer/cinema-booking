from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .models import SEAT_TYPE_MULTIPLIER, SeatType, SessionFormat, SessionLanguage, SessionStatus


class HallResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    rows: int
    seats_per_row: int


class CreateHallRequest(BaseModel):
    name: str
    rows: int
    seats_per_row: int


class SeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    row: int
    number: int
    seat_type: SeatType
    is_active: bool


class SeatWithAvailability(SeatResponse):
    is_booked: bool
    price: float


class UpdateSeatRequest(BaseModel):
    seat_type: SeatType | None = None
    is_active: bool | None = None


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movie_id: int
    hall_id: int
    start_time: datetime
    format: SessionFormat
    language: SessionLanguage
    base_price: float
    status: SessionStatus


class SessionDetailResponse(SessionResponse):
    seats: list[SeatWithAvailability]


class CreateSessionRequest(BaseModel):
    movie_id: int
    hall_id: int
    start_time: datetime
    format: SessionFormat = SessionFormat.TWO_D
    language: SessionLanguage = SessionLanguage.RU
    base_price: float


class UpdateSessionRequest(BaseModel):
    start_time: datetime | None = None
    format: SessionFormat | None = None
    language: SessionLanguage | None = None
    base_price: float | None = None
    status: SessionStatus | None = None
