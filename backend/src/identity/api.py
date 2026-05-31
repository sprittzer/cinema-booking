from typing import Any

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.models import Movie, MovieReview, ReviewLike
from src.common.dependencies import get_current_user, require_roles

from .models import User
from .scheme import (
    CreateAdminUserRequest,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UpdateUserAdminRequest,
    UserResponse,
    UserReviewResponse,
)
from .use_case import (
    CreateAdminUserUseCase,
    DeleteUserUseCase,
    GetHistoryUseCase,
    GetUsersUseCase,
    GetUserUseCase,
    LoginUseCase,
    RegisterUseCase,
    UpdateProfileUseCase,
    UpdateUserUseCase,
)

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register(
    data: RegisterRequest,
    use_case: FromDishka[RegisterUseCase],
) -> TokenResponse:
    return await use_case.execute(data)


@router.post("/auth/login", response_model=TokenResponse)
@inject
async def login(
    data: LoginRequest,
    use_case: FromDishka[LoginUseCase],
) -> TokenResponse:
    return await use_case.execute(data)


@router.get("/users/me", response_model=UserResponse)
@inject
async def get_me(
    session: FromDishka[AsyncSession],
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    result = await session.execute(
        select(func.count()).select_from(MovieReview).where(MovieReview.user_id == current_user.id)
    )
    reviews_count = result.scalar() or 0
    response = UserResponse.model_validate(current_user)
    response.reviews_count = reviews_count
    return response


@router.put("/users/me", response_model=UserResponse)
@inject
async def update_me(
    data: UpdateProfileRequest,
    use_case: FromDishka[UpdateProfileUseCase],
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return await use_case.execute(current_user, data)


@router.get("/users", response_model=list[UserResponse])
@inject
async def get_users(
    use_case: FromDishka[GetUsersUseCase],
    _: User = Depends(require_roles("admin")),
) -> list[UserResponse]:
    return await use_case.execute()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    data: CreateAdminUserRequest,
    use_case: FromDishka[CreateAdminUserUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> UserResponse:
    return await use_case.execute(data)


@router.get("/users/me/reviews", response_model=list[UserReviewResponse])
@inject
async def get_my_reviews(
    session: FromDishka[AsyncSession],
    current_user: User = Depends(get_current_user),
) -> list[UserReviewResponse]:
    result = await session.execute(
        select(
            MovieReview.id,
            MovieReview.movie_id,
            Movie.title.label("movie_title"),
            MovieReview.score,
            MovieReview.text,
            func.coalesce(func.sum(case((ReviewLike.value == 1, 1), else_=0)), 0).label("likes"),
            func.coalesce(func.sum(case((ReviewLike.value == -1, 1), else_=0)), 0).label("dislikes"),
        )
        .join(Movie, Movie.id == MovieReview.movie_id)
        .outerjoin(ReviewLike, ReviewLike.review_id == MovieReview.id)
        .where(MovieReview.user_id == current_user.id)
        .group_by(MovieReview.id, MovieReview.movie_id, Movie.title, MovieReview.score, MovieReview.text)
        .order_by(MovieReview.id.desc())
    )
    return [
        UserReviewResponse(
            id=row.id,
            movie_id=row.movie_id,
            movie_title=row.movie_title,
            score=row.score,
            text=row.text,
            likes=int(row.likes),
            dislikes=int(row.dislikes),
        )
        for row in result.all()
    ]


@router.get("/users/me/history")
@inject
async def get_history(
    use_case: FromDishka[GetHistoryUseCase],
    current_user: User = Depends(get_current_user),
) -> list[Any]:
    return await use_case.execute(current_user)


@router.get("/users/{user_id}", response_model=UserResponse)
@inject
async def get_user(
    user_id: int,
    use_case: FromDishka[GetUserUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> UserResponse:
    return await use_case.execute(user_id)


@router.put("/users/{user_id}", response_model=UserResponse)
@inject
async def update_user(
    user_id: int,
    data: UpdateUserAdminRequest,
    use_case: FromDishka[UpdateUserUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> UserResponse:
    return await use_case.execute(user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: int,
    use_case: FromDishka[DeleteUserUseCase],
    _: User = Depends(require_roles("admin")),
) -> None:
    await use_case.execute(user_id)
