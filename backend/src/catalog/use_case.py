import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_use_case import BaseUseCase
from src.common.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError
from src.identity.models import User

from .dao import ActorDAO, MovieDAO, MovieReviewDAO, ReviewLikeDAO
from .models import Actor, Movie, MovieReview, MovieStatus, ReviewLike
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
    UpdateActorRequest,
    UpdateMovieRequest,
)
from .tmdb_service import fetch_age_rating, fetch_credits, fetch_images, fetch_movie, fetch_person, fetch_trailer_url, map_genre


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
    def __init__(self, movie_dao: MovieDAO, actor_dao: ActorDAO) -> None:
        self._movie_dao = movie_dao
        self._actor_dao = actor_dao

    async def execute(self, data: ImportTMDBRequest) -> MovieResponse:
        if await self._movie_dao.get_by_tmdb_id(data.tmdb_id):
            raise AlreadyExistsError("Фильм уже импортирован")

        tmdb_data, trailer_url, age_rating, credits = await asyncio.gather(
            fetch_movie(data.tmdb_id),
            fetch_trailer_url(data.tmdb_id),
            fetch_age_rating(data.tmdb_id),
            fetch_credits(data.tmdb_id),
        )

        poster_path = tmdb_data.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        genre_ids = [g["id"] for g in tmdb_data.get("genres", [])]

        release_date = tmdb_data.get("release_date") or ""
        release_year = int(release_date[:4]) if len(release_date) >= 4 else None

        movie = Movie(
            title=tmdb_data["title"],
            description=tmdb_data.get("overview"),
            duration_minutes=tmdb_data.get("runtime"),
            genre=map_genre(genre_ids),
            age_rating=age_rating,
            poster_url=poster_url,
            trailer_url=trailer_url,
            tmdb_id=data.tmdb_id,
            tmdb_rating=tmdb_data.get("vote_average"),
            release_year=release_year,
        )
        movie = await self._movie_dao.create(movie)

        person_details = await asyncio.gather(
            *[fetch_person(c["tmdb_id"]) for c in credits],
            return_exceptions=True,
        )

        for cast_member, person in zip(credits, person_details):
            bio = person.get("biography") if isinstance(person, dict) else None
            birth_year_raw = person.get("birthday") if isinstance(person, dict) else None
            birth_year = int(birth_year_raw[:4]) if birth_year_raw and len(birth_year_raw) >= 4 else None

            actor = await self._actor_dao.get_by_tmdb_id(cast_member["tmdb_id"])
            if not actor:
                actor = Actor(
                    name=cast_member["name"],
                    photo_url=cast_member["photo_url"],
                    tmdb_id=cast_member["tmdb_id"],
                    bio=bio or None,
                    birth_year=birth_year,
                )
                actor = await self._actor_dao.create(actor)
            try:
                await self._actor_dao.add_to_movie(movie.id, actor.id, cast_member["character"])
            except Exception:
                pass

        return MovieResponse.model_validate(movie)


class GetMovieImagesUseCase(BaseUseCase):
    def __init__(self, dao: MovieDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int) -> list[str]:
        movie = await self._dao.get_by_id(movie_id)
        if not movie or not movie.tmdb_id:
            return []
        return await fetch_images(movie.tmdb_id)


class GetReviewsUseCase(BaseUseCase):
    def __init__(self, dao: MovieReviewDAO, like_dao: ReviewLikeDAO) -> None:
        self._dao = dao
        self._like_dao = like_dao

    async def execute(self, movie_id: int, current_user_id: int | None = None) -> list[ReviewResponse]:
        rows = await self._dao.get_by_movie(movie_id)
        counts = await self._like_dao.get_counts_for_movie(movie_id)
        reactions: dict[int, int] = {}
        if current_user_id:
            reactions = await self._like_dao.get_user_reactions_for_movie(movie_id, current_user_id)
        result = []
        for review, user_name in rows:
            r = ReviewResponse.model_validate(review)
            r.user_name = user_name
            likes, dislikes = counts.get(review.id, (0, 0))
            r.likes = likes
            r.dislikes = dislikes
            r.my_reaction = reactions.get(review.id)
            result.append(r)
        return result


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

        review = MovieReview(user_id=user.id, movie_id=movie_id, score=data.score, text=data.text)
        review = await self._review_dao.create(review)
        await self._movie_dao.recalculate_avg_rating(movie_id)
        response = ReviewResponse.model_validate(review)
        response.user_name = user.name
        return response


class DeleteReviewUseCase(BaseUseCase):
    def __init__(self, movie_dao: MovieDAO, review_dao: MovieReviewDAO) -> None:
        self._movie_dao = movie_dao
        self._review_dao = review_dao

    async def execute(self, review_id: int, user: User) -> None:
        review = await self._review_dao.get_by_id(review_id)
        if not review:
            raise NotFoundError("Отзыв не найден")
        if review.user_id != user.id and user.role.value != "admin":
            raise ForbiddenError("Нет доступа")
        await self._review_dao.delete(review)
        await self._movie_dao.recalculate_avg_rating(review.movie_id)


class ReactToReviewUseCase(BaseUseCase):
    def __init__(self, review_dao: MovieReviewDAO, like_dao: ReviewLikeDAO) -> None:
        self._review_dao = review_dao
        self._like_dao = like_dao

    async def execute(self, review_id: int, user: User, value: int) -> None:
        review = await self._review_dao.get_by_id(review_id)
        if not review:
            raise NotFoundError("Отзыв не найден")
        if review.user_id == user.id:
            raise ForbiddenError("Нельзя реагировать на собственный отзыв")
        existing = await self._like_dao.get_by_review_and_user(review_id, user.id)
        if existing:
            if existing.value == value:
                await self._like_dao.delete(existing)
            else:
                existing.value = value
                await self._like_dao.update(existing)
        else:
            await self._like_dao.create(ReviewLike(review_id=review_id, user_id=user.id, value=value))


class GetActorsUseCase(BaseUseCase):
    def __init__(self, dao: ActorDAO) -> None:
        self._dao = dao

    async def execute(self) -> list[ActorResponse]:
        actors = await self._dao.get_all()
        return [ActorResponse.model_validate(a) for a in actors]


class GetMovieActorsUseCase(BaseUseCase):
    def __init__(self, dao: ActorDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int) -> list[MovieActorResponse]:
        pairs = await self._dao.get_by_movie(movie_id)
        return [
            MovieActorResponse(
                id=actor.id,
                name=actor.name,
                photo_url=actor.photo_url,
                birth_year=actor.birth_year,
                character=character,
                bio=actor.bio,
            )
            for actor, character in pairs
        ]


class CreateActorUseCase(BaseUseCase):
    def __init__(self, dao: ActorDAO) -> None:
        self._dao = dao

    async def execute(self, data: CreateActorRequest) -> ActorResponse:
        actor = Actor(**data.model_dump())
        actor = await self._dao.create(actor)
        return ActorResponse.model_validate(actor)


class UpdateActorUseCase(BaseUseCase):
    def __init__(self, dao: ActorDAO) -> None:
        self._dao = dao

    async def execute(self, actor_id: int, data: UpdateActorRequest) -> ActorResponse:
        actor = await self._dao.get_by_id(actor_id)
        if not actor:
            raise NotFoundError("Актёр не найден")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(actor, field, value)
        actor = await self._dao.update(actor)
        return ActorResponse.model_validate(actor)


class DeleteActorUseCase(BaseUseCase):
    def __init__(self, dao: ActorDAO) -> None:
        self._dao = dao

    async def execute(self, actor_id: int) -> None:
        actor = await self._dao.get_by_id(actor_id)
        if not actor:
            raise NotFoundError("Актёр не найден")
        await self._dao.delete(actor)


class AddMovieActorUseCase(BaseUseCase):
    def __init__(self, actor_dao: ActorDAO, movie_dao: MovieDAO) -> None:
        self._actor_dao = actor_dao
        self._movie_dao = movie_dao

    async def execute(self, movie_id: int, data: AddMovieActorRequest) -> MovieActorResponse:
        if not await self._movie_dao.get_by_id(movie_id):
            raise NotFoundError("Фильм не найден")
        actor = await self._actor_dao.get_by_id(data.actor_id)
        if not actor:
            raise NotFoundError("Актёр не найден")
        try:
            await self._actor_dao.add_to_movie(movie_id, data.actor_id, data.character)
        except Exception:
            raise AlreadyExistsError("Актёр уже добавлен к фильму")
        return MovieActorResponse(
            id=actor.id,
            name=actor.name,
            photo_url=actor.photo_url,
            birth_year=actor.birth_year,
            character=data.character,
        )


class RemoveMovieActorUseCase(BaseUseCase):
    def __init__(self, dao: ActorDAO) -> None:
        self._dao = dao

    async def execute(self, movie_id: int, actor_id: int) -> None:
        await self._dao.remove_from_movie(movie_id, actor_id)
