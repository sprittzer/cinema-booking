from src.common.base_use_case import BaseUseCase
from src.common.exceptions import NotFoundError

from .dao import HallDAO, SeatDAO, SessionDAO
from .models import SEAT_TYPE_MULTIPLIER, CinemaSession, Hall, Seat
from .scheme import (
    CreateHallRequest,
    CreateSessionRequest,
    HallResponse,
    SeatResponse,
    SeatWithAvailability,
    SessionDetailResponse,
    SessionResponse,
    UpdateSeatRequest,
    UpdateSessionRequest,
)


class GetHallsUseCase(BaseUseCase):
    def __init__(self, dao: HallDAO) -> None:
        self._dao = dao

    async def execute(self) -> list[HallResponse]:
        halls = await self._dao.get_all()
        return [HallResponse.model_validate(h) for h in halls]


class CreateHallUseCase(BaseUseCase):
    def __init__(self, hall_dao: HallDAO, seat_dao: SeatDAO) -> None:
        self._hall_dao = hall_dao
        self._seat_dao = seat_dao

    async def execute(self, data: CreateHallRequest) -> HallResponse:
        hall = Hall(name=data.name, rows=data.rows, seats_per_row=data.seats_per_row)
        hall = await self._hall_dao.create(hall)

        seats = [
            Seat(hall_id=hall.id, row=row, number=num)
            for row in range(1, data.rows + 1)
            for num in range(1, data.seats_per_row + 1)
        ]
        await self._seat_dao.create_bulk(seats)
        return HallResponse.model_validate(hall)


class GetHallSeatsUseCase(BaseUseCase):
    def __init__(self, hall_dao: HallDAO, seat_dao: SeatDAO) -> None:
        self._hall_dao = hall_dao
        self._seat_dao = seat_dao

    async def execute(self, hall_id: int) -> list[SeatResponse]:
        if not await self._hall_dao.get_by_id(hall_id):
            raise NotFoundError("Зал не найден")
        seats = await self._seat_dao.get_by_hall(hall_id)
        return [SeatResponse.model_validate(s) for s in seats]


class UpdateSeatUseCase(BaseUseCase):
    def __init__(self, seat_dao: SeatDAO) -> None:
        self._seat_dao = seat_dao

    async def execute(self, seat_id: int, data: UpdateSeatRequest) -> SeatResponse:
        seat = await self._seat_dao.get_by_id(seat_id)
        if not seat:
            raise NotFoundError("Место не найдено")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(seat, field, value)
        seat = await self._seat_dao.update(seat)
        return SeatResponse.model_validate(seat)


class GetSessionsUseCase(BaseUseCase):
    def __init__(self, dao: SessionDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int | None = None) -> list[SessionResponse]:
        sessions = await self._dao.get_all(movie_id=movie_id)
        return [SessionResponse.model_validate(s) for s in sessions]


class GetSessionDetailUseCase(BaseUseCase):
    def __init__(self, session_dao: SessionDAO, seat_dao: SeatDAO) -> None:
        self._session_dao = session_dao
        self._seat_dao = seat_dao

    async def execute(self, session_id: int) -> SessionDetailResponse:
        cinema_session = await self._session_dao.get_by_id(session_id)
        if not cinema_session:
            raise NotFoundError("Сеанс не найден")

        seats = await self._seat_dao.get_by_hall(cinema_session.hall_id)
        booked_ids = await self._seat_dao.get_booked_seat_ids(session_id)

        seat_map = [
            SeatWithAvailability(
                id=s.id,
                row=s.row,
                number=s.number,
                seat_type=s.seat_type,
                is_active=s.is_active,
                is_booked=s.id in booked_ids,
                price=round(cinema_session.base_price * SEAT_TYPE_MULTIPLIER[s.seat_type], 2),
            )
            for s in seats
        ]

        return SessionDetailResponse(
            id=cinema_session.id,
            movie_id=cinema_session.movie_id,
            hall_id=cinema_session.hall_id,
            start_time=cinema_session.start_time,
            format=cinema_session.format,
            language=cinema_session.language,
            base_price=cinema_session.base_price,
            status=cinema_session.status,
            seats=seat_map,
        )


class CreateSessionUseCase(BaseUseCase):
    def __init__(self, session_dao: SessionDAO, hall_dao: HallDAO) -> None:
        self._session_dao = session_dao
        self._hall_dao = hall_dao

    async def execute(self, data: CreateSessionRequest) -> SessionResponse:
        if not await self._hall_dao.get_by_id(data.hall_id):
            raise NotFoundError("Зал не найден")
        cinema_session = CinemaSession(**data.model_dump())
        cinema_session = await self._session_dao.create(cinema_session)
        return SessionResponse.model_validate(cinema_session)


class UpdateSessionUseCase(BaseUseCase):
    def __init__(self, dao: SessionDAO) -> None:
        self._dao = dao

    async def execute(self, session_id: int, data: UpdateSessionRequest) -> SessionResponse:
        cinema_session = await self._dao.get_by_id(session_id)
        if not cinema_session:
            raise NotFoundError("Сеанс не найден")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(cinema_session, field, value)
        cinema_session = await self._dao.update(cinema_session)
        return SessionResponse.model_validate(cinema_session)


class CancelSessionUseCase(BaseUseCase):
    def __init__(self, dao: SessionDAO) -> None:
        self._dao = dao

    async def execute(self, session_id: int) -> None:
        cinema_session = await self._dao.get_by_id(session_id)
        if not cinema_session:
            raise NotFoundError("Сеанс не найден")
        await self._dao.cancel_with_bookings(cinema_session)
