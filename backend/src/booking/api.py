from dishka.integrations.fastapi import FromDI, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.common.dependencies import get_current_user, require_roles
from src.identity.models import User

from .scheme import (
    BookingDetailResponse,
    BookingResponse,
    CreateBookingRequest,
    PayBookingResponse,
    ScanTicketRequest,
    ScanTicketResponse,
)
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

router = APIRouter(tags=["bookings"])


@router.get("/bookings/me", response_model=list[BookingDetailResponse])
@inject
async def get_my_bookings(
    use_case: FromDI[GetMyBookingsUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> list[BookingDetailResponse]:
    return await use_case.execute(current_user)


@router.post("/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_booking(
    data: CreateBookingRequest,
    use_case: FromDI[CreateBookingUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> BookingResponse:
    return await use_case.execute(current_user, data)


@router.post("/bookings/{booking_id}/pay", response_model=PayBookingResponse)
@inject
async def pay_booking(
    booking_id: int,
    use_case: FromDI[PayBookingUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> PayBookingResponse:
    return await use_case.execute(booking_id, current_user)


@router.get("/bookings/{booking_id}/qr")
@inject
async def get_qr(
    booking_id: int,
    use_case: FromDI[GetQRUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    qr_base64 = await use_case.execute(booking_id, current_user)
    return JSONResponse({"qr_code": qr_base64})


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def cancel_booking(
    booking_id: int,
    use_case: FromDI[CancelBookingUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> None:
    await use_case.execute(booking_id, current_user)


@router.get("/bookings", response_model=list[BookingResponse])
@inject
async def get_all_bookings(
    use_case: FromDI[GetAllBookingsUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> list[BookingResponse]:
    return await use_case.execute()


@router.get("/bookings/session/{session_id}", response_model=list[BookingDetailResponse])
@inject
async def get_session_bookings(
    session_id: int,
    use_case: FromDI[GetSessionBookingsUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> list[BookingDetailResponse]:
    return await use_case.execute(session_id)


@router.post("/tickets/scan", response_model=ScanTicketResponse)
@inject
async def scan_ticket(
    data: ScanTicketRequest,
    use_case: FromDI[ScanTicketUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> ScanTicketResponse:
    return await use_case.execute(data)
