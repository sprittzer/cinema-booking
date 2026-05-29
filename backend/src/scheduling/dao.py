from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_dao import BaseDAO

from .models import CinemaSession, Hall, Seat, SessionStatus


class HallDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all(self) -> list[Hall]:
        result = await self._session.execute(select(Hall).order_by(Hall.id))
        return list(result.scalars().all())

    async def get_by_id(self, hall_id: int) -> Hall | None:
        result = await self._session.execute(select(Hall).where(Hall.id == hall_id))
        return result.scalar_one_or_none()

    async def create(self, hall: Hall) -> Hall:
        self._session.add(hall)
        await self._session.commit()
        await self._session.refresh(hall)
        return hall

    async def delete(self, hall: Hall) -> None:
        await self._session.delete(hall)
        await self._session.commit()


class SeatDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_hall(self, hall_id: int) -> list[Seat]:
        result = await self._session.execute(
            select(Seat).where(Seat.hall_id == hall_id).order_by(Seat.row, Seat.number)
        )
        return list(result.scalars().all())

    async def get_by_id(self, seat_id: int) -> Seat | None:
        result = await self._session.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def create_bulk(self, seats: list[Seat]) -> None:
        self._session.add_all(seats)
        await self._session.commit()

    async def update(self, seat: Seat) -> Seat:
        await self._session.commit()
        await self._session.refresh(seat)
        return seat

    async def get_booked_seat_ids(self, session_id: int) -> set[int]:
        from src.booking.models import Booking, BookingSeat, BookingStatus

        result = await self._session.execute(
            select(BookingSeat.seat_id)
            .join(Booking, Booking.id == BookingSeat.booking_id)
            .where(
                Booking.session_id == session_id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            )
        )
        return set(result.scalars().all())


class SessionDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all(self, movie_id: int | None = None) -> list[CinemaSession]:
        query = select(CinemaSession)
        if movie_id:
            query = query.where(CinemaSession.movie_id == movie_id)
        result = await self._session.execute(query.order_by(CinemaSession.start_time))
        return list(result.scalars().all())

    async def get_by_id(self, session_id: int) -> CinemaSession | None:
        result = await self._session.execute(select(CinemaSession).where(CinemaSession.id == session_id))
        return result.scalar_one_or_none()

    async def create(self, cinema_session: CinemaSession) -> CinemaSession:
        self._session.add(cinema_session)
        await self._session.commit()
        await self._session.refresh(cinema_session)
        return cinema_session

    async def update(self, cinema_session: CinemaSession) -> CinemaSession:
        await self._session.commit()
        await self._session.refresh(cinema_session)
        return cinema_session

    async def cancel_with_bookings(self, cinema_session: CinemaSession) -> None:
        from src.booking.models import Booking, BookingStatus

        result = await self._session.execute(
            select(Booking).where(
                Booking.session_id == cinema_session.id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            )
        )
        bookings = result.scalars().all()
        for booking in bookings:
            booking.status = BookingStatus.CANCELLED

        cinema_session.status = SessionStatus.CANCELLED
        await self._session.commit()
