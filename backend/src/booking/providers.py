from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .dao import BookingDAO
from .use_case import (
    CancelBookingUseCase,
    CreateBookingUseCase,
    GetAllBookingsUseCase,
    GetMyBookingsUseCase,
    GetQRUseCase,
    GetSessionBookingsUseCase,
    PayBookingUseCase,
    ScanTicketUseCase,
)


class BookingProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_booking_dao(self, session: AsyncSession) -> BookingDAO:
        return BookingDAO(session)

    @provide
    def create_booking_uc(self, dao: BookingDAO, session: AsyncSession) -> CreateBookingUseCase:
        return CreateBookingUseCase(dao, session)

    @provide
    def pay_booking_uc(self, dao: BookingDAO, session: AsyncSession) -> PayBookingUseCase:
        return PayBookingUseCase(dao, session)

    @provide
    def get_my_bookings_uc(self, dao: BookingDAO) -> GetMyBookingsUseCase:
        return GetMyBookingsUseCase(dao)

    @provide
    def get_all_bookings_uc(self, dao: BookingDAO) -> GetAllBookingsUseCase:
        return GetAllBookingsUseCase(dao)

    @provide
    def get_session_bookings_uc(self, dao: BookingDAO) -> GetSessionBookingsUseCase:
        return GetSessionBookingsUseCase(dao)

    @provide
    def get_qr_uc(self, dao: BookingDAO) -> GetQRUseCase:
        return GetQRUseCase(dao)

    @provide
    def cancel_booking_uc(self, dao: BookingDAO, session: AsyncSession) -> CancelBookingUseCase:
        return CancelBookingUseCase(dao, session)

    @provide
    def scan_ticket_uc(self, dao: BookingDAO) -> ScanTicketUseCase:
        return ScanTicketUseCase(dao)
