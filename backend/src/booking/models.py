import enum

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.common.base_model import BaseModel
from src.common.db import Base


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    USED = "used"
    CANCELLED = "cancelled"


class Booking(BaseModel):
    __tablename__ = "bookings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"))
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), default=BookingStatus.PENDING)
    ticket_code: Mapped[str | None] = mapped_column(String(36), unique=True, nullable=True)
    total_price: Mapped[float] = mapped_column(Float)


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), primary_key=True
    )
    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.id", ondelete="CASCADE"), primary_key=True
    )
