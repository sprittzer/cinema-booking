from typing import Literal

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
    tmdb_rating: float | None
    avg_rating: float | None
    release_year: int | None


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


class TMDBSearchResult(BaseModel):
    tmdb_id: int
    title: str
    year: str | None
    poster_url: str | None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    movie_id: int
    score: int
    text: str | None
    user_name: str | None = None
    likes: int = 0
    dislikes: int = 0
    my_reaction: int | None = None


class CreateReviewRequest(BaseModel):
    score: int = Field(ge=1, le=10)
    text: str | None = None


class ReactRequest(BaseModel):
    value: Literal[-1, 1]


class ActorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    photo_url: str | None
    birth_year: int | None
    bio: str | None


class MovieActorResponse(BaseModel):
    id: int
    name: str
    photo_url: str | None
    birth_year: int | None
    character: str | None
    bio: str | None = None


class CreateActorRequest(BaseModel):
    name: str
    photo_url: str | None = None
    birth_year: int | None = None
    bio: str | None = None


class UpdateActorRequest(BaseModel):
    name: str | None = None
    photo_url: str | None = None
    birth_year: int | None = None
    bio: str | None = None


class AddMovieActorRequest(BaseModel):
    actor_id: int
    character: str | None = None
