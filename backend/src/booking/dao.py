import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.models import Movie
from src.common.base_dao import BaseDAO
from src.identity.models import User
from src.scheduling.models import SEAT_TYPE_MULTIPLIER, CinemaSession, Hall, Seat

from .models import Booking, BookingSeat, BookingStatus
from .scheme import BookingDetailResponse, ScanTicketResponse, SeatInfo


class BookingDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, booking_id: int) -> Booking | None:
        result = await self._session.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()

    async def get_by_ticket_code(self, ticket_code: str) -> Booking | None:
        result = await self._session.execute(select(Booking).where(Booking.ticket_code == ticket_code))
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[Booking]:
        result = await self._session.execute(
            select(Booking).where(Booking.user_id == user_id).order_by(Booking.id.desc())
        )
        return list(result.scalars().all())

    async def get_by_session(self, session_id: int) -> list[Booking]:
        result = await self._session.execute(
            select(Booking).where(Booking.session_id == session_id).order_by(Booking.id)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Booking]:
        result = await self._session.execute(select(Booking).order_by(Booking.id.desc()))
        return list(result.scalars().all())

    async def get_seat_ids(self, booking_id: int) -> list[int]:
        result = await self._session.execute(select(BookingSeat.seat_id).where(BookingSeat.booking_id == booking_id))
        return list(result.scalars().all())

    async def check_seats_available(self, session_id: int, seat_ids: list[int]) -> list[int]:
        """Возвращает список уже занятых seat_ids."""
        result = await self._session.execute(
            select(BookingSeat.seat_id)
            .join(Booking, Booking.id == BookingSeat.booking_id)
            .where(
                Booking.session_id == session_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                BookingSeat.seat_id.in_(seat_ids),
            )
        )
        return list(result.scalars().all())

    async def create(self, booking: Booking, seat_ids: list[int]) -> Booking:
        self._session.add(booking)
        await self._session.flush()
        self._session.add_all([BookingSeat(booking_id=booking.id, seat_id=sid) for sid in seat_ids])
        await self._session.commit()
        await self._session.refresh(booking)
        return booking

    async def confirm(self, booking: Booking) -> tuple[Booking, str]:
        ticket_code = str(uuid.uuid4())
        booking.status = BookingStatus.CONFIRMED
        booking.ticket_code = ticket_code
        await self._session.commit()
        await self._session.refresh(booking)
        return booking, ticket_code

    async def update_status(self, booking: Booking, status: BookingStatus) -> Booking:
        booking.status = status
        await self._session.commit()
        await self._session.refresh(booking)
        return booking

    async def build_detail(self, booking: Booking) -> BookingDetailResponse:
        cinema_session = (
            await self._session.execute(select(CinemaSession).where(CinemaSession.id == booking.session_id))
        ).scalar_one()

        hall = (await self._session.execute(select(Hall).where(Hall.id == cinema_session.hall_id))).scalar_one()

        movie = (await self._session.execute(select(Movie).where(Movie.id == cinema_session.movie_id))).scalar_one()

        seat_ids = await self.get_seat_ids(booking.id)
        seats_result = await self._session.execute(select(Seat).where(Seat.id.in_(seat_ids)))
        seats = seats_result.scalars().all()

        seat_infos = [
            SeatInfo(
                id=s.id,
                row=s.row,
                number=s.number,
                seat_type=s.seat_type.value,
                price=round(cinema_session.base_price * SEAT_TYPE_MULTIPLIER[s.seat_type], 2),
            )
            for s in seats
        ]

        return BookingDetailResponse(
            id=booking.id,
            user_id=booking.user_id,
            session_id=booking.session_id,
            status=booking.status,
            ticket_code=booking.ticket_code,
            total_price=booking.total_price,
            movie_title=movie.title,
            start_time=cinema_session.start_time,
            hall_name=hall.name,
            seats=seat_infos,
        )

    async def build_scan_response(self, booking: Booking) -> ScanTicketResponse:
        detail = await self.build_detail(booking)
        user = (await self._session.execute(select(User).where(User.id == booking.user_id))).scalar_one()

        return ScanTicketResponse(
            booking_id=booking.id,
            movie_title=detail.movie_title,
            start_time=detail.start_time,
            hall_name=detail.hall_name,
            seats=detail.seats,
            user_name=user.name,
        )
