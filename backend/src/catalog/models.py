import enum

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.common.base_model import BaseModel


class Genre(str, enum.Enum):
    ACTION = "action"
    DRAMA = "drama"
    COMEDY = "comedy"
    HORROR = "horror"
    SCI_FI = "sci_fi"
    THRILLER = "thriller"
    ROMANCE = "romance"
    ANIMATION = "animation"
    DOCUMENTARY = "documentary"
    OTHER = "other"


class AgeRating(str, enum.Enum):
    G = "0+"
    PG6 = "6+"
    PG12 = "12+"
    PG16 = "16+"
    R = "18+"


class MovieStatus(str, enum.Enum):
    NOW_PLAYING = "now_playing"
    COMING_SOON = "coming_soon"
    ARCHIVED = "archived"


class Movie(BaseModel):
    __tablename__ = "movies"

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genre: Mapped[Genre | None] = mapped_column(Enum(Genre), nullable=True)
    age_rating: Mapped[AgeRating | None] = mapped_column(Enum(AgeRating), nullable=True)
    poster_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    trailer_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MovieStatus] = mapped_column(Enum(MovieStatus), default=MovieStatus.NOW_PLAYING)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    tmdb_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    avg_rating: Mapped[float | None] = mapped_column(Float, nullable=True)


class MovieReview(BaseModel):
    __tablename__ = "movie_reviews"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_user_movie_review"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(Integer)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
