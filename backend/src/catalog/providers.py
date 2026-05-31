from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .dao import ActorDAO, MovieDAO, MovieReviewDAO, ReviewLikeDAO
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


class CatalogProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_movie_dao(self, session: AsyncSession) -> MovieDAO:
        return MovieDAO(session)

    @provide
    def get_review_dao(self, session: AsyncSession) -> MovieReviewDAO:
        return MovieReviewDAO(session)

    @provide
    def get_review_like_dao(self, session: AsyncSession) -> ReviewLikeDAO:
        return ReviewLikeDAO(session)

    @provide
    def get_actor_dao(self, session: AsyncSession) -> ActorDAO:
        return ActorDAO(session)

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
    def import_tmdb_uc(self, dao: MovieDAO, actor_dao: ActorDAO) -> ImportTMDBUseCase:
        return ImportTMDBUseCase(dao, actor_dao)

    @provide
    def get_movie_images_uc(self, dao: MovieDAO) -> GetMovieImagesUseCase:
        return GetMovieImagesUseCase(dao)

    @provide
    def get_reviews_uc(self, dao: MovieReviewDAO, like_dao: ReviewLikeDAO) -> GetReviewsUseCase:
        return GetReviewsUseCase(dao, like_dao)

    @provide
    def create_review_uc(
        self, movie_dao: MovieDAO, review_dao: MovieReviewDAO, session: AsyncSession
    ) -> CreateReviewUseCase:
        return CreateReviewUseCase(movie_dao, review_dao, session)

    @provide
    def delete_review_uc(self, movie_dao: MovieDAO, review_dao: MovieReviewDAO) -> DeleteReviewUseCase:
        return DeleteReviewUseCase(movie_dao, review_dao)

    @provide
    def react_to_review_uc(self, review_dao: MovieReviewDAO, like_dao: ReviewLikeDAO) -> ReactToReviewUseCase:
        return ReactToReviewUseCase(review_dao, like_dao)

    @provide
    def get_actors_uc(self, dao: ActorDAO) -> GetActorsUseCase:
        return GetActorsUseCase(dao)

    @provide
    def get_movie_actors_uc(self, dao: ActorDAO) -> GetMovieActorsUseCase:
        return GetMovieActorsUseCase(dao)

    @provide
    def create_actor_uc(self, dao: ActorDAO) -> CreateActorUseCase:
        return CreateActorUseCase(dao)

    @provide
    def update_actor_uc(self, dao: ActorDAO) -> UpdateActorUseCase:
        return UpdateActorUseCase(dao)

    @provide
    def delete_actor_uc(self, dao: ActorDAO) -> DeleteActorUseCase:
        return DeleteActorUseCase(dao)

    @provide
    def add_movie_actor_uc(self, actor_dao: ActorDAO, movie_dao: MovieDAO) -> AddMovieActorUseCase:
        return AddMovieActorUseCase(actor_dao, movie_dao)

    @provide
    def remove_movie_actor_uc(self, dao: ActorDAO) -> RemoveMovieActorUseCase:
        return RemoveMovieActorUseCase(dao)
