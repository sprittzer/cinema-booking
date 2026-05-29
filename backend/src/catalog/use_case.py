from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_use_case import BaseUseCase
from src.common.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError
from src.identity.models import User

from .dao import MovieDAO, MovieReviewDAO
from .models import Movie, MovieReview, MovieStatus
from .scheme import (
    CreateMovieRequest,
    CreateReviewRequest,
    ImportTMDBRequest,
    MovieResponse,
    ReviewResponse,
    UpdateMovieRequest,
)
from .tmdb_service import fetch_movie, fetch_trailer_url, map_genre


class GetMoviesUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(
        self,
        genre: str | None = None,
        status: str | None = None,
        featured: bool | None = None,
    ) -> list[MovieResponse]:
        status_enum = MovieStatus(status) if status else None
        movies = await self._dao.get_all(genre=genre, status=status_enum, featured=featured)
        return [MovieResponse.model_validate(m) for m in movies]


class GetMovieUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int) -> MovieResponse:
        movie = await self._dao.get_by_id(movie_id)
        if not movie:
            raise NotFoundError("Фильм не найден")
        return MovieResponse.model_validate(movie)


class CreateMovieUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(self, data: CreateMovieRequest) -> MovieResponse:
        movie = Movie(**data.model_dump())
        movie = await self._dao.create(movie)
        return MovieResponse.model_validate(movie)


class UpdateMovieUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int, data: UpdateMovieRequest) -> MovieResponse:
        movie = await self._dao.get_by_id(movie_id)
        if not movie:
            raise NotFoundError("Фильм не найден")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(movie, field, value)
        movie = await self._dao.update(movie)
        return MovieResponse.model_validate(movie)


class DeleteMovieUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int) -> None:
        movie = await self._dao.get_by_id(movie_id)
        if not movie:
            raise NotFoundError("Фильм не найден")
        await self._dao.delete(movie)


class ImportTMDBUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(self, data: ImportTMDBRequest) -> MovieResponse:
        if await self._dao.get_by_tmdb_id(data.tmdb_id):
            raise AlreadyExistsError("Фильм уже импортирован")

        tmdb_data = await fetch_movie(data.tmdb_id)
        trailer_url = await fetch_trailer_url(data.tmdb_id)

        poster_path = tmdb_data.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        genre_ids = [g["id"] for g in tmdb_data.get("genres", [])]

        movie = Movie(
            title=tmdb_data["title"],
            description=tmdb_data.get("overview"),
            duration_minutes=tmdb_data.get("runtime"),
            genre=map_genre(genre_ids),
            poster_url=poster_url,
            trailer_url=trailer_url,
            tmdb_id=data.tmdb_id,
        )
        movie = await self._dao.create(movie)
        return MovieResponse.model_validate(movie)


class GetReviewsUseCase(BaseUseCase):
    def __init__(self, dao: MovieReviewDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int) -> list[ReviewResponse]:
        reviews = await self._dao.get_by_movie(movie_id)
        return [ReviewResponse.model_validate(r) for r in reviews]


class CreateReviewUseCase(BaseUseCase):
    def __init__(self, movie_dao: MovieDAO, review_dao: MovieReviewDAO, session: AsyncSession) -> None:
        self._movie_dao = movie_dao
        self._review_dao = review_dao
        self._session = session

    async def execute(self, movie_id: int, user: User, data: CreateReviewRequest) -> ReviewResponse:
        movie = await self._movie_dao.get_by_id(movie_id)
        if not movie:
            raise NotFoundError("Фильм не найден")

        if await self._review_dao.get_by_user_and_movie(user.id, movie_id):
            raise AlreadyExistsError("Отзыв уже оставлен")

        # проверяем что пользователь смотрел фильм
        from src.booking.models import Booking, BookingStatus
        from src.scheduling.models import CinemaSession

        watched = await self._session.execute(
            select(Booking).join(CinemaSession).where(
                Booking.user_id == user.id,
                Booking.status == BookingStatus.USED,
                CinemaSession.movie_id == movie_id,
            )
        )
        if not watched.scalar_one_or_none():
            raise ForbiddenError("Отзыв можно оставить только после просмотра")

        review = MovieReview(user_id=user.id, movie_id=movie_id, score=data.score, text=data.text)
        review = await self._review_dao.create(review)
        await self._movie_dao.recalculate_avg_rating(movie_id)
        return ReviewResponse.model_validate(review)


class DeleteReviewUseCase(BaseUseCase):
    def __init__(self, movie_dao: MovieDAO, review_dao: MovieReviewDAO) -> None:
        self._movie_dao = movie_dao
        self._review_dao = review_dao

    async def execute(self, review_id: int, user: User) -> None:
        review = await self._review_dao.get_by_id(review_id)
        if not review:
            raise NotFoundError("Отзыв не найден")
        if review.user_id != user.id and user.role.value not in ("moderator", "admin"):
            raise ForbiddenError("Нет доступа")
        await self._review_dao.delete(review)
        await self._movie_dao.recalculate_avg_rating(review.movie_id)
