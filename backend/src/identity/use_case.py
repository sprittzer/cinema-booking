from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_use_case import BaseUseCase
from src.common.exceptions import AlreadyExistsError, NotFoundError, UnauthorizedError
from src.common.security import create_access_token, hash_password, verify_password

from .dao import UserDAO
from .models import User
from .scheme import (
    CreateAdminUserRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UpdateUserAdminRequest,
    UserResponse,
)


class RegisterUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, data: RegisterRequest) -> TokenResponse:
        if await self._dao.get_by_email(data.email):
            raise AlreadyExistsError("Email уже используется")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            name=data.name,
        )
        user = await self._dao.create(user)
        return TokenResponse(access_token=create_access_token(user.id, user.role.value))


class LoginUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, data: LoginRequest) -> TokenResponse:
        user = await self._dao.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")

        return TokenResponse(access_token=create_access_token(user.id, user.role.value))


class GetUsersUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self) -> list[UserResponse]:
        users = await self._dao.get_all()
        return [UserResponse.model_validate(u) for u in users]


class UpdateProfileUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, user: User, data: UpdateProfileRequest) -> UserResponse:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        user = await self._dao.update(user)
        return UserResponse.model_validate(user)


class GetUserUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, user_id: int) -> UserResponse:
        user = await self._dao.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        return UserResponse.model_validate(user)


class CreateAdminUserUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, data: CreateAdminUserRequest) -> UserResponse:
        if await self._dao.get_by_email(data.email):
            raise AlreadyExistsError("Email уже используется")
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            name=data.name,
            role=data.role,
        )
        user = await self._dao.create(user)
        return UserResponse.model_validate(user)


class UpdateUserUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, user_id: int, data: UpdateUserAdminRequest) -> UserResponse:
        user = await self._dao.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        user = await self._dao.update(user)
        return UserResponse.model_validate(user)


class DeleteUserUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, user_id: int) -> None:
        user = await self._dao.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        await self._dao.delete(user)


class GetHistoryUseCase(BaseUseCase):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def execute(self, user: User) -> list[Any]:
        from src.booking.models import Booking, BookingStatus
        from src.catalog.models import Movie
        from src.catalog.scheme import MovieResponse
        from src.scheduling.models import CinemaSession

        result = await self._session.execute(
            select(Movie)
            .join(CinemaSession, CinemaSession.movie_id == Movie.id)
            .join(Booking, Booking.session_id == CinemaSession.id)
            .where(
                Booking.user_id == user.id,
                Booking.status == BookingStatus.USED,
            )
            .distinct()
            .order_by(Booking.updated_at.desc())
        )
        movies = result.scalars().all()
        return [MovieResponse.model_validate(m) for m in movies]
