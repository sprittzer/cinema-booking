from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_dao import BaseDAO
from src.identity.models import User

from .models import Actor, Movie, MovieReview, MovieStatus, ReviewLike, movie_actors


class MovieDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all(
        self,
        genre: str | None = None,
        status: MovieStatus | None = None,
        featured: bool | None = None,
    ) -> list[Movie]:
        query = select(Movie)
        if genre:
            query = query.where(Movie.genre == genre)
        if status:
            query = query.where(Movie.status == status)
        if featured is not None:
            query = query.where(Movie.is_featured == featured)
        result = await self._session.execute(query.order_by(Movie.id))
        return list(result.scalars().all())

    async def get_by_id(self, movie_id: int) -> Movie | None:
        result = await self._session.execute(select(Movie).where(Movie.id == movie_id))
        return result.scalar_one_or_none()

    async def get_by_tmdb_id(self, tmdb_id: int) -> Movie | None:
        result = await self._session.execute(select(Movie).where(Movie.tmdb_id == tmdb_id))
        return result.scalar_one_or_none()

    async def create(self, movie: Movie) -> Movie:
        self._session.add(movie)
        await self._session.commit()
        await self._session.refresh(movie)
        return movie

    async def update(self, movie: Movie) -> Movie:
        await self._session.commit()
        await self._session.refresh(movie)
        return movie

    async def delete(self, movie: Movie) -> None:
        await self._session.delete(movie)
        await self._session.commit()

    async def recalculate_avg_rating(self, movie_id: int) -> None:
        avg = await self._session.execute(select(func.avg(MovieReview.score)).where(MovieReview.movie_id == movie_id))
        new_avg = avg.scalar()
        await self._session.execute(update(Movie).where(Movie.id == movie_id).values(avg_rating=new_avg))
        await self._session.commit()


class MovieReviewDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_movie(self, movie_id: int) -> list[tuple[MovieReview, str | None]]:
        result = await self._session.execute(
            select(MovieReview, User.name)
            .join(User, User.id == MovieReview.user_id)
            .where(MovieReview.movie_id == movie_id)
            .order_by(MovieReview.id)
        )
        return list(result.tuples().all())

    async def get_by_id(self, review_id: int) -> MovieReview | None:
        result = await self._session.execute(select(MovieReview).where(MovieReview.id == review_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_movie(self, user_id: int, movie_id: int) -> MovieReview | None:
        result = await self._session.execute(
            select(MovieReview).where(
                MovieReview.user_id == user_id,
                MovieReview.movie_id == movie_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, review: MovieReview) -> MovieReview:
        self._session.add(review)
        await self._session.commit()
        await self._session.refresh(review)
        return review

    async def delete(self, review: MovieReview) -> None:
        await self._session.delete(review)
        await self._session.commit()


class ReviewLikeDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_review_and_user(self, review_id: int, user_id: int) -> ReviewLike | None:
        result = await self._session.execute(
            select(ReviewLike).where(
                ReviewLike.review_id == review_id,
                ReviewLike.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_counts_for_movie(self, movie_id: int) -> dict[int, tuple[int, int]]:
        result = await self._session.execute(
            select(
                ReviewLike.review_id,
                func.sum(case((ReviewLike.value == 1, 1), else_=0)).label("likes"),
                func.sum(case((ReviewLike.value == -1, 1), else_=0)).label("dislikes"),
            )
            .join(MovieReview, MovieReview.id == ReviewLike.review_id)
            .where(MovieReview.movie_id == movie_id)
            .group_by(ReviewLike.review_id)
        )
        return {row.review_id: (int(row.likes), int(row.dislikes)) for row in result.all()}

    async def get_user_reactions_for_movie(self, movie_id: int, user_id: int) -> dict[int, int]:
        result = await self._session.execute(
            select(ReviewLike.review_id, ReviewLike.value)
            .join(MovieReview, MovieReview.id == ReviewLike.review_id)
            .where(MovieReview.movie_id == movie_id, ReviewLike.user_id == user_id)
        )
        return {row.review_id: row.value for row in result.all()}

    async def create(self, like: ReviewLike) -> ReviewLike:
        self._session.add(like)
        await self._session.commit()
        await self._session.refresh(like)
        return like

    async def update(self, like: ReviewLike) -> ReviewLike:
        await self._session.commit()
        await self._session.refresh(like)
        return like

    async def delete(self, like: ReviewLike) -> None:
        await self._session.delete(like)
        await self._session.commit()


class ActorDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_all(self) -> list[Actor]:
        result = await self._session.execute(select(Actor).order_by(Actor.name))
        return list(result.scalars().all())

    async def get_by_id(self, actor_id: int) -> Actor | None:
        result = await self._session.execute(select(Actor).where(Actor.id == actor_id))
        return result.scalar_one_or_none()

    async def get_by_tmdb_id(self, tmdb_id: int) -> Actor | None:
        result = await self._session.execute(select(Actor).where(Actor.tmdb_id == tmdb_id))
        return result.scalar_one_or_none()

    async def create(self, actor: Actor) -> Actor:
        self._session.add(actor)
        await self._session.commit()
        await self._session.refresh(actor)
        return actor

    async def update(self, actor: Actor) -> Actor:
        await self._session.commit()
        await self._session.refresh(actor)
        return actor

    async def delete(self, actor: Actor) -> None:
        await self._session.delete(actor)
        await self._session.commit()

    async def get_by_movie(self, movie_id: int) -> list[tuple[Actor, str | None]]:
        result = await self._session.execute(
            select(Actor, movie_actors.c.character)
            .join(movie_actors, Actor.id == movie_actors.c.actor_id)
            .where(movie_actors.c.movie_id == movie_id)
            .order_by(Actor.name)
        )
        return list(result.tuples().all())

    async def add_to_movie(self, movie_id: int, actor_id: int, character: str | None) -> None:
        await self._session.execute(
            movie_actors.insert().values(movie_id=movie_id, actor_id=actor_id, character=character)
        )
        await self._session.commit()

    async def remove_from_movie(self, movie_id: int, actor_id: int) -> None:
        await self._session.execute(
            movie_actors.delete().where(
                movie_actors.c.movie_id == movie_id,
                movie_actors.c.actor_id == actor_id,
            )
        )
        await self._session.commit()
