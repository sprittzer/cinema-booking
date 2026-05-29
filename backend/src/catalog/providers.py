from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .dao import MovieDAO, MovieReviewDAO
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


class CatalogProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_movie_dao(self, session: AsyncSession) -> MovieDAO:
        return MovieDAO(session)

    @provide
    def get_review_dao(self, session: AsyncSession) -> MovieReviewDAO:
        return MovieReviewDAO(session)

    @provide
    def get_movies_uc(self, dao: MovieDAO) -> GetMoviesUseCase:
        return GetMoviesUseCase(dao)

    @provide
    def get_movie_uc(self, dao: MovieDAO) -> GetMovieUseCase:
        return GetMovieUseCase(dao)

    @provide
    def create_movie_uc(self, dao: MovieDAO) -> CreateMovieUseCase:
        return CreateMovieUseCase(dao)

    @provide
    def update_movie_uc(self, dao: MovieDAO) -> UpdateMovieUseCase:
        return UpdateMovieUseCase(dao)

    @provide
    def delete_movie_uc(self, dao: MovieDAO) -> DeleteMovieUseCase:
        return DeleteMovieUseCase(dao)

    @provide
    def import_tmdb_uc(self, dao: MovieDAO) -> ImportTMDBUseCase:
        return ImportTMDBUseCase(dao)

    @provide
    def get_reviews_uc(self, dao: MovieReviewDAO) -> GetReviewsUseCase:
        return GetReviewsUseCase(dao)

    @provide
    def create_review_uc(
        self, movie_dao: MovieDAO, review_dao: MovieReviewDAO, session: AsyncSession
    ) -> CreateReviewUseCase:
        return CreateReviewUseCase(movie_dao, review_dao, session)

    @provide
    def delete_review_uc(self, movie_dao: MovieDAO, review_dao: MovieReviewDAO) -> DeleteReviewUseCase:
        return DeleteReviewUseCase(movie_dao, review_dao)
