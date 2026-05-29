from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, status

from src.common.dependencies import get_current_user, require_roles
from src.identity.models import User

from .models import Genre, MovieStatus
from .scheme import (
    CreateMovieRequest,
    CreateReviewRequest,
    ImportTMDBRequest,
    MovieResponse,
    ReviewResponse,
    UpdateMovieRequest,
)
from .use_case import (
    CreateMovieUseCase,
    CreateReviewUseCase,
    DeleteMovieUseCase,
    DeleteReviewUseCase,
    GetMoviesUseCase,
    GetMovieUseCase,
    GetReviewsUseCase,
    ImportTMDBUseCase,
    UpdateMovieUseCase,
)

router = APIRouter(prefix="/movies", tags=["movies"])


@router.get("", response_model=list[MovieResponse])
@inject
async def get_movies(
    genre: Genre | None = None,
    status: MovieStatus | None = None,
    featured: bool | None = None,
    use_case: FromDishka[GetMoviesUseCase] = ...,
) -> list[MovieResponse]:
    return await use_case.execute(genre=genre, status=status, featured=featured)


@router.get("/{movie_id}", response_model=MovieResponse)
@inject
async def get_movie(
    movie_id: int,
    use_case: FromDishka[GetMovieUseCase] = ...,
) -> MovieResponse:
    return await use_case.execute(movie_id)


@router.post("", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_movie(
    data: CreateMovieRequest,
    use_case: FromDishka[CreateMovieUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> MovieResponse:
    return await use_case.execute(data)


@router.put("/{movie_id}", response_model=MovieResponse)
@inject
async def update_movie(
    movie_id: int,
    data: UpdateMovieRequest,
    use_case: FromDishka[UpdateMovieUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> MovieResponse:
    return await use_case.execute(movie_id, data)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_movie(
    movie_id: int,
    use_case: FromDishka[DeleteMovieUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> None:
    await use_case.execute(movie_id)


@router.post("/import/tmdb", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
@inject
async def import_from_tmdb(
    data: ImportTMDBRequest,
    use_case: FromDishka[ImportTMDBUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> MovieResponse:
    return await use_case.execute(data)


@router.get("/{movie_id}/reviews", response_model=list[ReviewResponse])
@inject
async def get_reviews(
    movie_id: int,
    use_case: FromDishka[GetReviewsUseCase] = ...,
) -> list[ReviewResponse]:
    return await use_case.execute(movie_id)


@router.post("/{movie_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_review(
    movie_id: int,
    data: CreateReviewRequest,
    use_case: FromDishka[CreateReviewUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> ReviewResponse:
    return await use_case.execute(movie_id, current_user, data)


@router.delete("/{movie_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_review(
    movie_id: int,
    review_id: int,
    use_case: FromDishka[DeleteReviewUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> None:
    await use_case.execute(review_id, current_user)
