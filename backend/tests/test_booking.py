from unittest.mock import AsyncMock, MagicMock

import pytest

from src.booking.models import Booking, BookingStatus
from src.booking.scheme import CreateBookingRequest, ScanTicketRequest
from src.booking.use_case import CancelBookingUseCase, CreateBookingUseCase, ScanTicketUseCase
from src.common.exceptions import ForbiddenError, NotFoundError
from src.scheduling.models import Seat, SeatType, SessionStatus


class TestCreateBookingUseCase:
    async def test_create_booking_success(self, mock_booking_dao, mock_session_db, user, scheduled_session):
        seat = Seat()
        seat.id = 1
        seat.hall_id = 1
        seat.row = 1
        seat.number = 5
        seat.seat_type = SeatType.STANDARD
        seat.is_active = True

        seats_result = MagicMock()
        seats_result.scalars.return_value.all.return_value = [seat]

        mock_session_db.execute.return_value.scalar_one_or_none.return_value = scheduled_session
        mock_session_db.execute.return_value = seats_result

        # первый execute — сеанс, второй — места
        mock_session_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: scheduled_session),
            seats_result,
        ]

        mock_booking_dao.check_seats_available.return_value = []
        created = Booking()
        created.id = 1
        created.user_id = user.id
        created.session_id = scheduled_session.id
        created.status = BookingStatus.PENDING
        created.ticket_code = None
        created.total_price = 300.0
        mock_booking_dao.create.return_value = created

        use_case = CreateBookingUseCase(mock_booking_dao, mock_session_db)
        result = await use_case.execute(user, CreateBookingRequest(session_id=1, seat_ids=[1]))

        assert result.status == BookingStatus.PENDING
        assert result.total_price == 300.0

    async def test_session_not_found(self, mock_booking_dao, mock_session_db, user):
        from unittest.mock import MagicMock
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = None
        mock_session_db.execute = AsyncMock(return_value=execute_result)

        use_case = CreateBookingUseCase(mock_booking_dao, mock_session_db)
        with pytest.raises(NotFoundError):
            await use_case.execute(user, CreateBookingRequest(session_id=99, seat_ids=[1]))

    async def test_seats_already_taken(self, mock_booking_dao, mock_session_db, user, scheduled_session):
        seat = Seat()
        seat.id = 1
        seat.hall_id = 1
        seat.row = 1
        seat.number = 1
        seat.seat_type = SeatType.STANDARD
        seat.is_active = True

        seats_result = MagicMock()
        seats_result.scalars.return_value.all.return_value = [seat]

        mock_session_db.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: scheduled_session),
            seats_result,
        ]
        mock_booking_dao.check_seats_available.return_value = [1]

        use_case = CreateBookingUseCase(mock_booking_dao, mock_session_db)
        with pytest.raises(ForbiddenError):
            await use_case.execute(user, CreateBookingRequest(session_id=1, seat_ids=[1]))


class TestScanTicketUseCase:
    async def test_scan_success(self, mock_booking_dao):
        booking = Booking()
        booking.id = 1
        booking.status = BookingStatus.CONFIRMED
        booking.ticket_code = "some-uuid"
        mock_booking_dao.get_by_ticket_code.return_value = booking
        mock_booking_dao.update_status.return_value = booking
        mock_booking_dao.build_scan_response.return_value = MagicMock()

        use_case = ScanTicketUseCase(mock_booking_dao)
        await use_case.execute(ScanTicketRequest(ticket_code="some-uuid"))

        mock_booking_dao.update_status.assert_called_once_with(booking, BookingStatus.USED)

    async def test_scan_already_used(self, mock_booking_dao):
        booking = Booking()
        booking.id = 1
        booking.status = BookingStatus.USED
        booking.ticket_code = "some-uuid"
        mock_booking_dao.get_by_ticket_code.return_value = booking

        use_case = ScanTicketUseCase(mock_booking_dao)
        with pytest.raises(ForbiddenError):
            await use_case.execute(ScanTicketRequest(ticket_code="some-uuid"))

    async def test_scan_ticket_not_found(self, mock_booking_dao):
        mock_booking_dao.get_by_ticket_code.return_value = None

        use_case = ScanTicketUseCase(mock_booking_dao)
        with pytest.raises(NotFoundError):
            await use_case.execute(ScanTicketRequest(ticket_code="invalid"))


class TestCancelBookingUseCase:
    async def test_cancel_someone_elses_booking(self, mock_booking_dao, mock_session_db, user):
        booking = Booking()
        booking.id = 1
        booking.user_id = 999
        booking.status = BookingStatus.CONFIRMED
        mock_booking_dao.get_by_id.return_value = booking

        use_case = CancelBookingUseCase(mock_booking_dao, mock_session_db)
        with pytest.raises(ForbiddenError):
            await use_case.execute(1, user)

    async def test_cancel_used_booking(self, mock_booking_dao, mock_session_db, user):
        booking = Booking()
        booking.id = 1
        booking.user_id = user.id
        booking.status = BookingStatus.USED
        mock_booking_dao.get_by_id.return_value = booking

        use_case = CancelBookingUseCase(mock_booking_dao, mock_session_db)
        with pytest.raises(ForbiddenError):
            await use_case.execute(1, user)
