from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .dao import HallDAO, SeatDAO, SessionDAO
from .use_case import (
    CancelSessionUseCase,
    CreateHallUseCase,
    CreateSessionUseCase,
    DeleteHallUseCase,
    GetHallSeatsUseCase,
    GetHallUseCase,
    GetHallsUseCase,
    GetSessionDetailUseCase,
    GetSessionsUseCase,
    UpdateSeatUseCase,
    UpdateSessionUseCase,
)


class SchedulingProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_hall_dao(self, session: AsyncSession) -> HallDAO:
        return HallDAO(session)

    @provide
    def get_seat_dao(self, session: AsyncSession) -> SeatDAO:
        return SeatDAO(session)

    @provide
    def get_session_dao(self, session: AsyncSession) -> SessionDAO:
        return SessionDAO(session)

    @provide
    def get_halls_uc(self, dao: HallDAO) -> GetHallsUseCase:
        return GetHallsUseCase(dao)

    @provide
    def get_hall_uc(self, dao: HallDAO) -> GetHallUseCase:
        return GetHallUseCase(dao)

    @provide
    def create_hall_uc(self, hall_dao: HallDAO, seat_dao: SeatDAO) -> CreateHallUseCase:
        return CreateHallUseCase(hall_dao, seat_dao)

    @provide
    def get_hall_seats_uc(self, hall_dao: HallDAO, seat_dao: SeatDAO) -> GetHallSeatsUseCase:
        return GetHallSeatsUseCase(hall_dao, seat_dao)

    @provide
    def update_seat_uc(self, dao: SeatDAO) -> UpdateSeatUseCase:
        return UpdateSeatUseCase(dao)

    @provide
    def get_sessions_uc(self, dao: SessionDAO) -> GetSessionsUseCase:
        return GetSessionsUseCase(dao)

    @provide
    def get_session_detail_uc(self, session_dao: SessionDAO, seat_dao: SeatDAO) -> GetSessionDetailUseCase:
        return GetSessionDetailUseCase(session_dao, seat_dao)

    @provide
    def create_session_uc(self, session_dao: SessionDAO, hall_dao: HallDAO) -> CreateSessionUseCase:
        return CreateSessionUseCase(session_dao, hall_dao)

    @provide
    def update_session_uc(self, dao: SessionDAO) -> UpdateSessionUseCase:
        return UpdateSessionUseCase(dao)

    @provide
    def delete_hall_uc(self, dao: HallDAO) -> DeleteHallUseCase:
        return DeleteHallUseCase(dao)

    @provide
    def cancel_session_uc(self, dao: SessionDAO) -> CancelSessionUseCase:
        return CancelSessionUseCase(dao)
