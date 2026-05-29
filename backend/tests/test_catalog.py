import pytest

from src.catalog.models import Movie
from src.catalog.scheme import CreateMovieRequest, CreateReviewRequest
from src.catalog.use_case import CreateMovieUseCase, CreateReviewUseCase, GetMoviesUseCase
from src.common.exceptions import AlreadyExistsError, ForbiddenError, NotFoundError


class TestGetMoviesUseCase:
    async def test_returns_movie_list(self, mock_movie_dao):
        movie = Movie()
        movie.id = 1
        movie.title = "Inception"
        movie.description = None
        movie.duration_minutes = 148
        movie.genre = None
        movie.age_rating = None
        movie.poster_url = None
        movie.trailer_url = None
        movie.status = __import__("src.catalog.models", fromlist=["MovieStatus"]).MovieStatus.NOW_PLAYING
        movie.is_featured = False
        movie.avg_rating = None
        mock_movie_dao.get_all.return_value = [movie]

        use_case = GetMoviesUseCase(mock_movie_dao)
        result = await use_case.execute()

        assert len(result) == 1
        assert result[0].title == "Inception"

    async def test_returns_empty_list(self, mock_movie_dao):
        mock_movie_dao.get_all.return_value = []

        use_case = GetMoviesUseCase(mock_movie_dao)
        result = await use_case.execute()

        assert result == []


class TestCreateMovieUseCase:
    async def test_create_movie_success(self, mock_movie_dao):
        MovieStatus = __import__("src.catalog.models", fromlist=["MovieStatus"]).MovieStatus
        created = Movie()
        created.id = 1
        created.title = "Dune"
        created.description = None
        created.duration_minutes = 155
        created.genre = None
        created.age_rating = None
        created.poster_url = None
        created.trailer_url = None
        created.status = MovieStatus.NOW_PLAYING
        created.is_featured = False
        created.avg_rating = None
        mock_movie_dao.create.return_value = created

        use_case = CreateMovieUseCase(mock_movie_dao)
        result = await use_case.execute(
            CreateMovieRequest(title="Dune", duration_minutes=155)
        )

        assert result.title == "Dune"
        mock_movie_dao.create.assert_called_once()


class TestCreateReviewUseCase:
    async def test_review_without_viewing_is_forbidden(self, mock_movie_dao, mock_review_dao, mock_session_db, user):
        from unittest.mock import AsyncMock, MagicMock

        from src.catalog.models import Movie as MovieModel
        movie = MovieModel()
        movie.id = 1
        mock_movie_dao.get_by_id.return_value = movie
        mock_review_dao.get_by_user_and_movie.return_value = None

        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = None
        mock_session_db.execute = AsyncMock(return_value=execute_result)

        use_case = CreateReviewUseCase(mock_movie_dao, mock_review_dao, mock_session_db)
        with pytest.raises(ForbiddenError):
            await use_case.execute(1, user, CreateReviewRequest(score=5))

    async def test_duplicate_review_raises_error(self, mock_movie_dao, mock_review_dao, mock_session_db, user):
        from src.catalog.models import Movie as MovieModel, MovieReview
        movie = MovieModel()
        movie.id = 1
        mock_movie_dao.get_by_id.return_value = movie

        existing = MovieReview()
        mock_review_dao.get_by_user_and_movie.return_value = existing

        use_case = CreateReviewUseCase(mock_movie_dao, mock_review_dao, mock_session_db)
        with pytest.raises(AlreadyExistsError):
            await use_case.execute(1, user, CreateReviewRequest(score=4))

    async def test_movie_not_found_raises_error(self, mock_movie_dao, mock_review_dao, mock_session_db, user):
        mock_movie_dao.get_by_id.return_value = None

        use_case = CreateReviewUseCase(mock_movie_dao, mock_review_dao, mock_session_db)
        with pytest.raises(NotFoundError):
            await use_case.execute(99, user, CreateReviewRequest(score=3))
