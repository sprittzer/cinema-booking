from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.base_dao import BaseDAO

from .models import Movie, MovieReview, MovieStatus


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
        avg = await self._session.execute(
            select(func.avg(MovieReview.score)).where(MovieReview.movie_id == movie_id)
        )
        new_avg = avg.scalar()
        await self._session.execute(
            update(Movie).where(Movie.id == movie_id).values(avg_rating=new_avg)
        )
        await self._session.commit()


class MovieReviewDAO(BaseDAO):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_movie(self, movie_id: int) -> list[MovieReview]:
        result = await self._session.execute(
            select(MovieReview).where(MovieReview.movie_id == movie_id).order_by(MovieReview.id)
        )
        return list(result.scalars().all())

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
