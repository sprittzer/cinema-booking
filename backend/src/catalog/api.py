from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, status

from src.common.dependencies import get_current_user, get_optional_user, require_roles
from src.identity.models import User

from .models import Genre, MovieStatus
from .scheme import (
    ActorResponse,
    AddMovieActorRequest,
    CreateActorRequest,
    CreateMovieRequest,
    CreateReviewRequest,
    ImportTMDBRequest,
    MovieActorResponse,
    MovieResponse,
    ReactRequest,
    ReviewResponse,
    TMDBSearchResult,
    UpdateActorRequest,
    UpdateMovieRequest,
)
from .tmdb_service import search_movies
from .use_case import (
    AddMovieActorUseCase,
    CreateActorUseCase,
    CreateMovieUseCase,
    CreateReviewUseCase,
    DeleteActorUseCase,
    DeleteMovieUseCase,
    DeleteReviewUseCase,
    GetActorsUseCase,
    GetMovieActorsUseCase,
    GetMovieImagesUseCase,
    GetMoviesUseCase,
    GetMovieUseCase,
    GetReviewsUseCase,
    ImportTMDBUseCase,
    ReactToReviewUseCase,
    RemoveMovieActorUseCase,
    UpdateActorUseCase,
    UpdateMovieUseCase,
)

router = APIRouter(prefix="/movies", tags=["movies"])
actors_router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("", response_model=list[MovieResponse])
@inject
async def get_movies(
    genre: Genre | None = None,
    status: MovieStatus | None = None,
    featured: bool | None = None,
    use_case: FromDishka[GetMoviesUseCase] = ...,
) -> list[MovieResponse]:
    return await use_case.execute(genre=genre, status=status, featured=featured)


@router.get("/search/tmdb", response_model=list[TMDBSearchResult])
async def search_tmdb_movies(
    query: str,
    _: User = Depends(require_roles("admin")),
) -> list[TMDBSearchResult]:
    try:
        results = await search_movies(query)
        return [TMDBSearchResult(**r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"TMDB недоступен: {e}") from e


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


@router.get("/{movie_id}/images", response_model=list[str])
@inject
async def get_movie_images(
    movie_id: int,
    use_case: FromDishka[GetMovieImagesUseCase] = ...,
) -> list[str]:
    try:
        return await use_case.execute(movie_id)
    except Exception:
        return []


@router.get("/{movie_id}/actors", response_model=list[MovieActorResponse])
@inject
async def get_movie_actors(
    movie_id: int,
    use_case: FromDishka[GetMovieActorsUseCase] = ...,
) -> list[MovieActorResponse]:
    return await use_case.execute(movie_id)


@router.post("/{movie_id}/actors", response_model=MovieActorResponse, status_code=status.HTTP_201_CREATED)
@inject
async def add_movie_actor(
    movie_id: int,
    data: AddMovieActorRequest,
    use_case: FromDishka[AddMovieActorUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> MovieActorResponse:
    return await use_case.execute(movie_id, data)


@router.delete("/{movie_id}/actors/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_movie_actor(
    movie_id: int,
    actor_id: int,
    use_case: FromDishka[RemoveMovieActorUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> None:
    await use_case.execute(movie_id, actor_id)


@router.get("/{movie_id}/reviews", response_model=list[ReviewResponse])
@inject
async def get_reviews(
    movie_id: int,
    use_case: FromDishka[GetReviewsUseCase] = ...,
    current_user: User | None = Depends(get_optional_user),
) -> list[ReviewResponse]:
    return await use_case.execute(movie_id, current_user_id=current_user.id if current_user else None)


@router.post("/{movie_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_review(
    movie_id: int,
    data: CreateReviewRequest,
    use_case: FromDishka[CreateReviewUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> ReviewResponse:
    return await use_case.execute(movie_id, current_user, data)


@router.post("/{movie_id}/reviews/{review_id}/react", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def react_to_review(
    movie_id: int,
    review_id: int,
    data: ReactRequest,
    use_case: FromDishka[ReactToReviewUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> None:
    await use_case.execute(review_id, current_user, data.value)


@router.delete("/{movie_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_review(
    movie_id: int,
    review_id: int,
    use_case: FromDishka[DeleteReviewUseCase] = ...,
    current_user: User = Depends(get_current_user),
) -> None:
    await use_case.execute(review_id, current_user)


# --- Actors CRUD (admin) ---

@actors_router.get("", response_model=list[ActorResponse])
@inject
async def get_actors(
    use_case: FromDishka[GetActorsUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> list[ActorResponse]:
    return await use_case.execute()


@actors_router.post("", response_model=ActorResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_actor(
    data: CreateActorRequest,
    use_case: FromDishka[CreateActorUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> ActorResponse:
    return await use_case.execute(data)


@actors_router.get("/{actor_id}", response_model=ActorResponse)
@inject
async def get_actor(
    actor_id: int,
    use_case: FromDishka[GetActorsUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> ActorResponse:
    actors = await use_case.execute()
    actor = next((a for a in actors if a.id == actor_id), None)
    if not actor:
        raise HTTPException(status_code=404, detail="Актёр не найден")
    return actor


@actors_router.put("/{actor_id}", response_model=ActorResponse)
@inject
async def update_actor(
    actor_id: int,
    data: UpdateActorRequest,
    use_case: FromDishka[UpdateActorUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> ActorResponse:
    return await use_case.execute(actor_id, data)


@actors_router.delete("/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_actor(
    actor_id: int,
    use_case: FromDishka[DeleteActorUseCase] = ...,
    _: User = Depends(require_roles("admin")),
) -> None:
    await use_case.execute(actor_id)
