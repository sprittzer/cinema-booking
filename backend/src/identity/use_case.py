from src.common.base_use_case import BaseUseCase
from src.common.exceptions import AlreadyExistsError, NotFoundError, UnauthorizedError
from src.common.security import create_access_token, hash_password, verify_password

from .dao import UserDAO
from .models import User
from .scheme import LoginRequest, RegisterRequest, TokenResponse, UpdateProfileRequest, UserResponse


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


class DeleteUserUseCase(BaseUseCase):
    def __init__(self, dao: UserDAO) -> None:
        self._dao = dao

    async def execute(self, user_id: int) -> None:
        user = await self._dao.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        await self._dao.delete(user)
