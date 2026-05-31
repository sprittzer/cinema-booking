import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, CalendarDays, ChevronLeft, ChevronRight, Clock, Star, ThumbsDown, ThumbsUp, Trash2 } from "lucide-react";
import Header from "../components/Header";
import { createReview, deleteReview, getMovieActors, getMovieById, getMovieImages, getMyBookings, getReviews, getSessions, reactToReview } from "../api/api";
import { formatSessionTime } from "../utils/date";
import { getCurrentUser, hasRole } from "../utils/storage";

const HERO_DESC_LIMIT = 260;

function ScorePicker({ value, onChange }) {
  const [hovered, setHovered] = useState(0);
  const active = hovered || value;

  return (
    <div className="score-picker" onMouseLeave={() => setHovered(0)}>
      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((n) => (
        <button
          key={n}
          type="button"
          className="score-star"
          onMouseEnter={() => setHovered(n)}
          onClick={() => onChange(n)}
        >
          <Star
            size={26}
            fill={n <= active ? "var(--gold)" : "none"}
            color={n <= active ? "var(--gold)" : "var(--line)"}
            strokeWidth={1.5}
          />
        </button>
      ))}
      {active > 0 && <span className="score-label">{active}/10</span>}
    </div>
  );
}

function ReviewScore({ score }) {
  return (
    <span className="review-score-badge">
      <Star size={11} fill="currentColor" /> {score}/10
    </span>
  );
}

export default function MoviePage() {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const timerRef = useRef(null);
  const actorsRowRef = useRef(null);
  const currentUser = getCurrentUser();
  const isStaff = hasRole(currentUser, ["admin"]);

  const [movie, setMovie] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [images, setImages] = useState([]);
  const [actors, setActors] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [myBookings, setMyBookings] = useState([]);
  const [activeSlide, setActiveSlide] = useState(0);
  const [error, setError] = useState("");

  const [reviewScore, setReviewScore] = useState(0);
  const [reviewText, setReviewText] = useState("");
  const [reviewSaving, setReviewSaving] = useState(false);
  const [reviewError, setReviewError] = useState("");

  useEffect(() => {
    Promise.all([
      getMovieById(movieId),
      getSessions(movieId),
      getMovieImages(movieId),
      getMovieActors(movieId),
      getReviews(movieId),
      (currentUser && !isStaff) ? getMyBookings() : Promise.resolve([]),
    ])
      .then(([movieData, sessionData, imageData, actorData, reviewData, bookingsData]) => {
        setMovie(movieData);
        setSessions(sessionData);
        setImages(imageData);
        setActors(actorData);
        setReviews(reviewData);
        setMyBookings(bookingsData);
      })
      .catch(() => setError("Не удалось загрузить фильм"));
  }, [movieId]);

  useEffect(() => {
    if (images.length <= 1) return;
    timerRef.current = setInterval(
      () => setActiveSlide((p) => (p + 1) % images.length),
      5000
    );
    return () => clearInterval(timerRef.current);
  }, [images.length]);

  const goTo = (i) => {
    setActiveSlide(i);
    clearInterval(timerRef.current);
    if (images.length > 1) {
      timerRef.current = setInterval(
        () => setActiveSlide((p) => (p + 1) % images.length),
        5000
      );
    }
  };

  const ourRating = useMemo(() => {
    if (!reviews.length) return null;
    return reviews.reduce((sum, r) => sum + r.score, 0) / reviews.length;
  }, [reviews]);

  const userReview = useMemo(
    () => reviews.find((r) => r.user_id === currentUser?.id),
    [reviews, currentUser]
  );

  const canReview = useMemo(
    () => myBookings.some(
      (b) => b.movieTitle === movie?.title && (b.status === "confirmed" || b.status === "used")
    ),
    [myBookings, movie]
  );


  async function handleSubmitReview(e) {
    e.preventDefault();
    if (!reviewScore) { setReviewError("Выберите оценку"); return; }
    setReviewSaving(true);
    setReviewError("");
    try {
      await createReview(movieId, { score: reviewScore, text: reviewText || null });
      const updated = await getReviews(movieId);
      setReviews(updated);
      setReviewScore(0);
      setReviewText("");
    } catch (err) {
      setReviewError(err.message || "Не удалось отправить отзыв");
    } finally {
      setReviewSaving(false);
    }
  }

  async function handleReact(reviewId, value) {
    try {
      await reactToReview(movieId, reviewId, value);
      const updated = await getReviews(movieId);
      setReviews(updated);
    } catch {
      // silent
    }
  }

  async function handleDeleteReview(reviewId) {
    try {
      await deleteReview(movieId, reviewId);
      setReviews((prev) => prev.filter((r) => r.id !== reviewId));
    } catch {
      setReviewError("Не удалось удалить отзыв");
    }
  }

  const trailerEmbed = movie?.trailer_url
    ? movie.trailer_url.replace("watch?v=", "embed/") + "?rel=0&modestbranding=1"
    : null;

  const hasLongDesc = movie?.description && movie.description.length > HERO_DESC_LIMIT;
  const showBody = trailerEmbed || hasLongDesc || actors.length > 0 || true;

  if (!movie) {
    return (
      <>
        <Header />
        <div style={{ padding: "60px 40px", color: "var(--muted)" }}>Загрузка...</div>
      </>
    );
  }

  return (
    <>
      <Header />

      <section className="movie-hero">
        {images.map((url, i) => (
          <div
            key={i}
            className={`backdrop-slide${i === activeSlide ? " active" : ""}`}
            style={{ backgroundImage: `url(${url})` }}
          />
        ))}
        {images.length === 0 && movie.posterUrl && (
          <div
            className="backdrop-slide active"
            style={{ backgroundImage: `url(${movie.posterUrl})`, filter: "blur(2px) brightness(0.6)" }}
          />
        )}
        <div className="movie-hero-overlay" />

        {images.length > 1 && (
          <div className="hero-nav">
            <div className="slide-dots">
              {images.map((_, i) => (
                <button
                  key={i}
                  className={`slide-dot${i === activeSlide ? " active" : ""}`}
                  onClick={() => goTo(i)}
                />
              ))}
            </div>
          </div>
        )}

        <div className="movie-hero-body">
          <button className="back-btn" onClick={() => navigate("/afisha")}>
            <ArrowLeft size={20} />
          </button>

          <div className="movie-hero-grid">
            <div className="movie-hero-poster">
              <img src={movie.posterUrl || "/poster-fallback.jpg"} alt={movie.title} />
              {movie.ageLimit && (
                <span
                  className={`age-badge age-${movie.ageLimit.replace("+", "")}`}
                  style={{ top: 14, right: 14 }}
                >
                  {movie.ageLimit}
                </span>
              )}
            </div>

            <div className="movie-hero-info">
              <span className="overline">О фильме</span>
              <h1>{movie.title}</h1>

              <div className="movie-meta-row">
                <span>
                  <Star size={14} fill="currentColor" />
                  <span data-tooltip="TMDB">
                    {movie.tmdbRating != null ? movie.tmdbRating.toFixed(1) : "—"}
                  </span>
                  <em className="rating-sep">/</em>
                  <span data-tooltip={ourRating != null ? `Зрители (${reviews.length} отз.)` : "Зрители"}>
                    {ourRating != null ? ourRating.toFixed(1) : "—"}
                  </span>
                </span>
                <span><Clock size={15} /> {movie.duration || 120} мин</span>
                {movie.genre && <span>{movie.genre}</span>}
                {movie.ageLimit && <span>{movie.ageLimit}</span>}
              </div>

              <p className="movie-description-full">
                {hasLongDesc
                  ? movie.description.slice(0, HERO_DESC_LIMIT) + "…"
                  : movie.description}
              </p>

              <div className="nearest-sessions">
                <h2>Ближайшие сеансы</h2>
                {sessions.length === 0 ? (
                  <p style={{ color: "rgba(255,255,255,0.45)", fontSize: 14, margin: 0 }}>
                    Сеансов пока нет
                  </p>
                ) : (
                  <div className="details-session-list">
                    {sessions.slice(0, 4).map((session) => (
                      <span key={session.id} className="details-session-chip">
                        <CalendarDays size={13} /> {formatSessionTime(session.time, session.dateStr)} · зал {session.hall}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {!isStaff && movie.status !== "coming_soon" && (
                <Link to={`/movies/${movie.id}/booking`} className="primary-btn details-book-btn">
                  Посмотреть сеансы <ChevronRight size={18} />
                </Link>
              )}
              {movie.status === "coming_soon" && (
                <div className="coming-soon-badge">Скоро в кино</div>
              )}
            </div>
          </div>
        </div>
      </section>

      {showBody && (
        <div className="movie-body">
          <div className="movie-body-inner">
            {actors.length > 0 && (
              <section className="movie-actors">
                <div className="actors-header">
                  <h2>В ролях</h2>
                  <div className="actors-nav">
                    <button className="actors-nav-btn" onClick={() => actorsRowRef.current?.scrollBy({ left: -360, behavior: "smooth" })}><ChevronLeft size={18} /></button>
                    <button className="actors-nav-btn" onClick={() => actorsRowRef.current?.scrollBy({ left: 360, behavior: "smooth" })}><ChevronRight size={18} /></button>
                  </div>
                </div>
                <div className="actors-row" ref={actorsRowRef}>
                  {actors.map((actor) => (
                    <div key={actor.id} className="actor-card">
                      <div className="actor-photo">
                        {actor.photo_url
                          ? <img src={actor.photo_url} alt={actor.name} />
                          : <div className="actor-photo-placeholder" />
                        }
                      </div>
                      <div className="actor-name">{actor.name}</div>
                      {actor.character && <div className="actor-character">{actor.character}</div>}
                      {(actor.bio || actor.birth_year) && (
                        <div className="actor-tooltip">
                          <div className="actor-tooltip-name">{actor.name}</div>
                          {actor.character && <div className="actor-tooltip-char">{actor.character}</div>}
                          {actor.birth_year && <div className="actor-tooltip-year">{actor.birth_year} г.р.</div>}
                          {actor.bio && <p className="actor-tooltip-bio">{actor.bio.slice(0, 220)}{actor.bio.length > 220 ? "…" : ""}</p>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}

            {hasLongDesc && (
              <section className="movie-full-desc">
                <h2>О фильме</h2>
                <p className="movie-description-full">{movie.description}</p>
              </section>
            )}

            {trailerEmbed && (
              <section className="movie-trailer">
                <h2>Трейлер</h2>
                <div className="trailer-frame">
                  <iframe
                    src={trailerEmbed}
                    title="Трейлер"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                </div>
              </section>
            )}

            <section className="movie-reviews">
              <div className="reviews-header">
                <h2>Отзывы</h2>
                {reviews.length > 0 && (
                  <span className="reviews-count">{reviews.length}</span>
                )}
              </div>

              {reviews.length === 0 && (
                <p className="reviews-empty">Отзывов пока нет. Купите билет и поделитесь впечатлениями после просмотра.</p>
              )}

              <div className="reviews-list">
                {reviews.map((review) => {
                  const isOwn = review.user_id === currentUser?.id;
                  return (
                    <div key={review.id} className={`review-card${isOwn ? " own" : ""}`}>
                      <div className="review-card-top">
                        <div className="review-author-info">
                          <div className="review-avatar">
                            {isOwn
                              ? currentUser?.name?.[0]?.toUpperCase()
                              : review.user_name?.[0]?.toUpperCase() || "З"}
                          </div>
                          <div>
                            <div className="review-author-name">
                              {isOwn ? (currentUser?.name || "Вы") : (review.user_name || "Зритель")}
                            </div>
                            <ReviewScore score={review.score} />
                          </div>
                        </div>
                        {isOwn && (
                          <button
                            className="icon-btn review-delete-btn"
                            onClick={() => handleDeleteReview(review.id)}
                            title="Удалить отзыв"
                          >
                            <Trash2 size={15} />
                          </button>
                        )}
                      </div>
                      {review.text && <p className="review-text">{review.text}</p>}
                      <div className="review-reactions">
                        <button
                          className={`reaction-btn${review.my_reaction === 1 ? " active-like" : ""}`}
                          onClick={() => handleReact(review.id, 1)}
                          disabled={isOwn || !currentUser}
                          title="Нравится"
                        >
                          <ThumbsUp size={13} />
                          {review.likes > 0 && <span>{review.likes}</span>}
                        </button>
                        <button
                          className={`reaction-btn${review.my_reaction === -1 ? " active-dislike" : ""}`}
                          onClick={() => handleReact(review.id, -1)}
                          disabled={isOwn || !currentUser}
                          title="Не нравится"
                        >
                          <ThumbsDown size={13} />
                          {review.dislikes > 0 && <span>{review.dislikes}</span>}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>

              {!userReview && canReview && (
                <form className="review-form" onSubmit={handleSubmitReview}>
                  <h3>Ваш отзыв</h3>
                  <ScorePicker value={reviewScore} onChange={setReviewScore} />
                  <textarea
                    className="input review-textarea"
                    placeholder="Напишите пару слов о фильме (необязательно)"
                    value={reviewText}
                    onChange={(e) => setReviewText(e.target.value)}
                    rows={3}
                  />
                  {reviewError && <div className="alert error" style={{ marginBottom: 0 }}>{reviewError}</div>}
                  <button className="primary-btn" type="submit" disabled={reviewSaving}>
                    {reviewSaving ? "Отправка..." : "Отправить отзыв"}
                  </button>
                </form>
              )}
            </section>
          </div>
        </div>
      )}

      {error && (
        <div style={{ padding: "16px 40px" }}>
          <div className="alert error">{error}</div>
        </div>
      )}
    </>
  );
}
