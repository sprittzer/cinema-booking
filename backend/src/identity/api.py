from dishka.integrations.fastapi import FromDI, inject
from fastapi import APIRouter, Depends, status

from src.common.dependencies import get_current_user, require_roles

from .models import User
from .scheme import LoginRequest, RegisterRequest, TokenResponse, UpdateProfileRequest, UserResponse
from .use_case import DeleteUserUseCase, GetUsersUseCase, LoginUseCase, RegisterUseCase, UpdateProfileUseCase

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register(
    data: RegisterRequest,
    use_case: FromDI[RegisterUseCase],
) -> TokenResponse:
    return await use_case.execute(data)


@router.post("/auth/login", response_model=TokenResponse)
@inject
async def login(
    data: LoginRequest,
    use_case: FromDI[LoginUseCase],
) -> TokenResponse:
    return await use_case.execute(data)


@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.put("/users/me", response_model=UserResponse)
@inject
async def update_me(
    data: UpdateProfileRequest,
    use_case: FromDI[UpdateProfileUseCase],
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return await use_case.execute(current_user, data)


@router.get("/users", response_model=list[UserResponse])
@inject
async def get_users(
    use_case: FromDI[GetUsersUseCase],
    _: User = Depends(require_roles("admin")),
) -> list[UserResponse]:
    return await use_case.execute()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: int,
    use_case: FromDI[DeleteUserUseCase],
    _: User = Depends(require_roles("admin")),
) -> None:
    await use_case.execute(user_id)
