from dishka.integrations.fastapi import FromDI, inject
from fastapi import APIRouter, Depends, status

from src.common.dependencies import get_current_user, require_roles
from src.identity.models import User

from .scheme import (
    CreateHallRequest,
    CreateSessionRequest,
    HallResponse,
    SeatResponse,
    SessionDetailResponse,
    SessionResponse,
    UpdateSeatRequest,
    UpdateSessionRequest,
)
from .use_case import (
    CancelSessionUseCase,
    CreateHallUseCase,
    CreateSessionUseCase,
    GetHallSeatsUseCase,
    GetHallsUseCase,
    GetSessionDetailUseCase,
    GetSessionsUseCase,
    UpdateSeatUseCase,
    UpdateSessionUseCase,
)

halls_router = APIRouter(prefix="/halls", tags=["halls"])
sessions_router = APIRouter(prefix="/sessions", tags=["sessions"])


@halls_router.get("", response_model=list[HallResponse])
@inject
async def get_halls(
    use_case: FromDI[GetHallsUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> list[HallResponse]:
    return await use_case.execute()


@halls_router.post("", response_model=HallResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_hall(
    data: CreateHallRequest,
    use_case: FromDI[CreateHallUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> HallResponse:
    return await use_case.execute(data)


@halls_router.get("/{hall_id}/seats", response_model=list[SeatResponse])
@inject
async def get_hall_seats(
    hall_id: int,
    use_case: FromDI[GetHallSeatsUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> list[SeatResponse]:
    return await use_case.execute(hall_id)


@halls_router.put("/{hall_id}/seats/{seat_id}", response_model=SeatResponse)
@inject
async def update_seat(
    hall_id: int,
    seat_id: int,
    data: UpdateSeatRequest,
    use_case: FromDI[UpdateSeatUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> SeatResponse:
    return await use_case.execute(seat_id, data)


@sessions_router.get("", response_model=list[SessionResponse])
@inject
async def get_sessions(
    movie_id: int | None = None,
    use_case: FromDI[GetSessionsUseCase] = ...,
) -> list[SessionResponse]:
    return await use_case.execute(movie_id=movie_id)


@sessions_router.get("/{session_id}", response_model=SessionDetailResponse)
@inject
async def get_session(
    session_id: int,
    use_case: FromDI[GetSessionDetailUseCase] = ...,
) -> SessionDetailResponse:
    return await use_case.execute(session_id)


@sessions_router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_session(
    data: CreateSessionRequest,
    use_case: FromDI[CreateSessionUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> SessionResponse:
    return await use_case.execute(data)


@sessions_router.put("/{session_id}", response_model=SessionResponse)
@inject
async def update_session(
    session_id: int,
    data: UpdateSessionRequest,
    use_case: FromDI[UpdateSessionUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> SessionResponse:
    return await use_case.execute(session_id, data)


@sessions_router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def cancel_session(
    session_id: int,
    use_case: FromDI[CancelSessionUseCase] = ...,
    _: User = Depends(require_roles("admin", "moderator")),
) -> None:
    await use_case.execute(session_id)
