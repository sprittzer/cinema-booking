import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.common.base_model import BaseModel


class SeatType(enum.StrEnum):
    STANDARD = "standard"
    VIP = "vip"
    COUPLE = "couple"


SEAT_TYPE_MULTIPLIER = {
    SeatType.STANDARD: 1.0,
    SeatType.VIP: 1.5,
    SeatType.COUPLE: 2.0,
}


class SessionFormat(enum.StrEnum):
    TWO_D = "2d"
    THREE_D = "3d"
    IMAX = "imax"


class SessionLanguage(enum.StrEnum):
    RU = "ru"
    EN = "en"
    EN_SUB = "en_sub"


class SessionStatus(enum.StrEnum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Hall(BaseModel):
    __tablename__ = "halls"

    name: Mapped[str] = mapped_column(String(100))
    rows: Mapped[int] = mapped_column(Integer)
    seats_per_row: Mapped[int] = mapped_column(Integer)


class Seat(BaseModel):
    __tablename__ = "seats"

    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id", ondelete="CASCADE"))
    row: Mapped[int] = mapped_column(Integer)
    number: Mapped[int] = mapped_column(Integer)
    seat_type: Mapped[SeatType] = mapped_column(Enum(SeatType), default=SeatType.STANDARD)
    is_active: Mapped[bool] = mapped_column(default=True)


class CinemaSession(BaseModel):
    __tablename__ = "sessions"

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    hall_id: Mapped[int] = mapped_column(ForeignKey("halls.id", ondelete="CASCADE"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    format: Mapped[SessionFormat] = mapped_column(Enum(SessionFormat), default=SessionFormat.TWO_D)
    language: Mapped[SessionLanguage] = mapped_column(Enum(SessionLanguage), default=SessionLanguage.RU)
    base_price: Mapped[float] = mapped_column(Float)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus), default=SessionStatus.SCHEDULED)
