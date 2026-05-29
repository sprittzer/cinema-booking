from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_use_case import BaseUseCase
from src.common.exceptions import ForbiddenError, NotFoundError
from src.identity.models import User
from src.scheduling.models import SEAT_TYPE_MULTIPLIER, CinemaSession, Seat, SessionStatus

from .dao import BookingDAO
from .email_service import send_booking_confirmation
from .models import Booking, BookingStatus
from .qr_service import generate_qr_base64
from .scheme import (
    BookingDetailResponse,
    BookingResponse,
    CreateBookingRequest,
    PayBookingResponse,
    ScanTicketRequest,
    ScanTicketResponse,
)


class CreateBookingUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO, session: AsyncSession) -> None:
        self._dao = dao
        self._session = session

    async def execute(self, user: User, data: CreateBookingRequest) -> BookingResponse:
        cinema_session = (
            await self._session.execute(select(CinemaSession).where(CinemaSession.id == data.session_id))
        ).scalar_one_or_none()

        if not cinema_session:
            raise NotFoundError("Сеанс не найден")
        if cinema_session.status != SessionStatus.SCHEDULED:
            raise ForbiddenError("Сеанс недоступен для бронирования")

        seats_result = await self._session.execute(
            select(Seat).where(
                Seat.id.in_(data.seat_ids),
                Seat.hall_id == cinema_session.hall_id,
                Seat.is_active == True,  # noqa: E712
            )
        )
        seats = seats_result.scalars().all()

        if len(seats) != len(data.seat_ids):
            raise ForbiddenError("Одно или несколько мест недоступны")

        taken = await self._dao.check_seats_available(data.session_id, data.seat_ids)
        if taken:
            raise ForbiddenError("Одно или несколько мест уже заняты")

        total_price = sum(round(cinema_session.base_price * SEAT_TYPE_MULTIPLIER[s.seat_type], 2) for s in seats)

        booking = Booking(
            user_id=user.id,
            session_id=data.session_id,
            total_price=total_price,
        )
        booking = await self._dao.create(booking, data.seat_ids)
        return BookingResponse.model_validate(booking)


class PayBookingUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO, session: AsyncSession) -> None:
        self._dao = dao
        self._session = session

    async def execute(self, booking_id: int, user: User) -> PayBookingResponse:
        booking = await self._dao.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Бронирование не найдено")
        if booking.user_id != user.id:
            raise ForbiddenError("Нет доступа")
        if booking.status != BookingStatus.PENDING:
            raise ForbiddenError("Бронирование уже обработано")

        booking, ticket_code = await self._dao.confirm(booking)
        qr_code = generate_qr_base64(ticket_code)

        detail = await self._dao.build_detail(booking)
        seats_str = ", ".join(f"Ряд {s.row} Место {s.number}" for s in detail.seats)

        await send_booking_confirmation(
            to_email=user.email,
            user_name=user.name,
            movie_title=detail.movie_title,
            start_time=detail.start_time.strftime("%d.%m.%Y %H:%M"),
            hall_name=detail.hall_name,
            seats=seats_str,
            ticket_code=ticket_code,
            qr_base64=qr_code,
        )

        return PayBookingResponse(
            id=booking.id,
            user_id=booking.user_id,
            session_id=booking.session_id,
            status=booking.status,
            ticket_code=booking.ticket_code,
            total_price=booking.total_price,
            qr_code=qr_code,
        )


class GetMyBookingsUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO) -> None:
        self._dao = dao

    async def execute(self, user: User) -> list[BookingDetailResponse]:
        bookings = await self._dao.get_by_user(user.id)
        return [await self._dao.build_detail(b) for b in bookings]


class GetAllBookingsUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO) -> None:
        self._dao = dao

    async def execute(self) -> list[BookingResponse]:
        bookings = await self._dao.get_all()
        return [BookingResponse.model_validate(b) for b in bookings]


class GetSessionBookingsUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO) -> None:
        self._dao = dao

    async def execute(self, session_id: int) -> list[BookingDetailResponse]:
        bookings = await self._dao.get_by_session(session_id)
        return [await self._dao.build_detail(b) for b in bookings]


class GetQRUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO) -> None:
        self._dao = dao

    async def execute(self, booking_id: int, user: User) -> str:
        booking = await self._dao.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Бронирование не найдено")
        if booking.user_id != user.id:
            raise ForbiddenError("Нет доступа")
        if not booking.ticket_code:
            raise ForbiddenError("Билет ещё не оплачен")
        return generate_qr_base64(booking.ticket_code)


class CancelBookingUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO, session: AsyncSession) -> None:
        self._dao = dao
        self._session = session

    async def execute(self, booking_id: int, user: User) -> None:
        booking = await self._dao.get_by_id(booking_id)
        if not booking:
            raise NotFoundError("Бронирование не найдено")
        if booking.user_id != user.id:
            raise ForbiddenError("Нет доступа")
        if booking.status in (BookingStatus.USED, BookingStatus.CANCELLED):
            raise ForbiddenError("Нельзя отменить это бронирование")

        cinema_session = (
            await self._session.execute(select(CinemaSession).where(CinemaSession.id == booking.session_id))
        ).scalar_one()

        if datetime.now(UTC) >= cinema_session.start_time.replace(tzinfo=UTC):
            raise ForbiddenError("Сеанс уже начался")

        await self._dao.update_status(booking, BookingStatus.CANCELLED)


class ScanTicketUseCase(BaseUseCase):
    def __init__(self, dao: BookingDAO) -> None:
        self._dao = dao

    async def execute(self, data: ScanTicketRequest) -> ScanTicketResponse:
        booking = await self._dao.get_by_ticket_code(data.ticket_code)
        if not booking:
            raise NotFoundError("Билет не найден")
        if booking.status == BookingStatus.USED:
            raise ForbiddenError("Билет уже использован")
        if booking.status != BookingStatus.CONFIRMED:
            raise ForbiddenError("Билет недействителен")

        await self._dao.update_status(booking, BookingStatus.USED)
        return await self._dao.build_scan_response(booking)
