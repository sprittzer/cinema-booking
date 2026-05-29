from pydantic import BaseModel, ConfigDict, Field

from .models import AgeRating, Genre, MovieStatus


class MovieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    duration_minutes: int | None
    genre: Genre | None
    age_rating: AgeRating | None
    poster_url: str | None
    trailer_url: str | None
    status: MovieStatus
    is_featured: bool
    avg_rating: float | None


class CreateMovieRequest(BaseModel):
    title: str
    description: str | None = None
    duration_minutes: int | None = None
    genre: Genre | None = None
    age_rating: AgeRating | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    status: MovieStatus = MovieStatus.NOW_PLAYING
    is_featured: bool = False


class UpdateMovieRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    genre: Genre | None = None
    age_rating: AgeRating | None = None
    poster_url: str | None = None
    trailer_url: str | None = None
    status: MovieStatus | None = None
    is_featured: bool | None = None


class ImportTMDBRequest(BaseModel):
    tmdb_id: int


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    movie_id: int
    score: int
    text: str | None


class CreateReviewRequest(BaseModel):
    score: int = Field(ge=1, le=5)
    text: str | None = None
