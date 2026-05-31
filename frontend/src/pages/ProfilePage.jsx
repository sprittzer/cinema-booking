import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CalendarDays, Check, Film, MapPin, Pencil, Star, ThumbsDown, ThumbsUp, X } from "lucide-react";
import Header from "../components/Header";
import { getMe, getMyBookings, getMyReviews, updateMe } from "../api/api";
import { getCurrentUser, hasRole, initials, saveCurrentUser } from "../utils/storage";

const STATUS_LABELS = {
  pending: "Не оплачено",
  confirmed: "Оплачено",
  cancelled: "Отменено",
  used: "Использован",
};

function pluralSeats(n) {
  if (n === 1) return "место";
  if (n >= 2 && n <= 4) return "места";
  return "мест";
}

export default function ProfilePage() {
  const [user, setUser] = useState(getCurrentUser());
  const isStaff = hasRole(user, ["admin"]);
  const [bookings, setBookings] = useState([]);
  const [myReviews, setMyReviews] = useState([]);
  const [reviewsError, setReviewsError] = useState("");
  const [error, setError] = useState("");
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({ name: "" });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getMe()
      .then((u) => { saveCurrentUser(u); setUser(u); })
      .catch(() => {});
    if (!isStaff) {
      getMyBookings()
        .then(setBookings)
        .catch(() => setError("Не удалось загрузить брони"));
      getMyReviews()
        .then(setMyReviews)
        .catch(() => setReviewsError("Не удалось загрузить отзывы"));
    }
  }, []);

  useEffect(() => {
    if (user) setForm({ name: user.name || "" });
  }, [user]);

  const spent = useMemo(() => bookings.reduce((sum, b) => sum + (b.total_price || 0), 0), [bookings]);
  const uniqueFilms = useMemo(() => new Set(bookings.map((b) => b.movieTitle).filter(Boolean)).size, [bookings]);

  async function saveProfile(event) {
    event.preventDefault();
    setSaving(true);
    try {
      const updated = await updateMe(form);
      saveCurrentUser(updated);
      setUser(updated);
      setEditMode(false);
    } catch (err) {
      setError(err.message || "Не удалось сохранить");
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <Header />
      <main className="profile-page">

        <div className="profile-header-card">
          <div className="profile-avatar-lg">{initials(user?.name)}</div>

          <div className="profile-header-info">
            {editMode ? (
              <form onSubmit={saveProfile} className="inline-name-form">
                <input
                  className="input inline-name-input"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  autoFocus
                />
                <button type="submit" className="icon-btn inline-name-btn" disabled={saving} title="Сохранить">
                  <Check size={16} />
                </button>
                <button type="button" className="icon-btn inline-name-btn" onClick={() => setEditMode(false)} title="Отмена">
                  <X size={16} />
                </button>
              </form>
            ) : (
              <div className="profile-name-row">
                <h1 className="profile-name">{user?.name || "Пользователь"}</h1>
                <button
                  className="icon-btn profile-edit-inline-btn"
                  onClick={() => setEditMode(true)}
                  title="Изменить имя"
                >
                  <Pencil size={15} />
                </button>
              </div>
            )}

            <p className="profile-email">{user?.email}</p>

            {!isStaff && (
              <div className="profile-header-stats">
                <div className="profile-stat">
                  <b>{bookings.length}</b>
                  <span>билетов</span>
                </div>
                <div className="profile-stat-divider" />
                <div className="profile-stat">
                  <b>{uniqueFilms}</b>
                  <span>фильмов</span>
                </div>
                <div className="profile-stat-divider" />
                <div className="profile-stat">
                  <b>{user?.reviews_count ?? 0}</b>
                  <span>отзывов</span>
                </div>
                <div className="profile-stat-divider" />
                <div className="profile-stat">
                  <b>{spent.toFixed(0)} ₽</b>
                  <span>потрачено</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {error && <div className="alert error" style={{ marginBottom: 20 }}>{error}</div>}

        {!isStaff && <h2 className="history-title" style={{ marginTop: 35 }}>Мои билеты</h2>}

        {!isStaff && <section className="ticket-list">
          {bookings.length === 0 && !error && (
            <div className="profile-empty">
              <Film size={40} />
              <p>Брони пока нет. Выберите фильм и забронируйте места.</p>
            </div>
          )}

          {bookings.map((booking) => (
            <article className="ticket-card" key={booking.id}>
              <div className="ticket-poster">
                <Film size={22} />
              </div>

              <div className="ticket-info">
                <div className="ticket-top-row">
                  <h3>{booking.movieTitle || `Сеанс ${booking.sessionId}`}</h3>
                  <span className={`status-badge status-${booking.status}`}>
                    {STATUS_LABELS[booking.status] || booking.status}
                  </span>
                </div>
                <p>
                  <CalendarDays size={13} />
                  {booking.sessionDate} · {booking.sessionTime}
                  {booking.hall_name ? <><MapPin size={13} style={{ marginLeft: 6 }} />{booking.hall_name}</> : null}
                </p>
                <div className="ticket-seats">
                  {(booking.seats || []).map((seat) => (
                    <span key={seat.id}>{String.fromCharCode(64 + seat.row)}-{seat.number}</span>
                  ))}
                </div>
              </div>

              <div className="ticket-price">
                <b>{booking.total_price} ₽</b>
                <span>{booking.seats?.length || 0} {pluralSeats(booking.seats?.length || 0)}</span>
              </div>
            </article>
          ))}
        </section>}

        {!isStaff && <h2 className="history-title" style={{ marginTop: 35 }}>Мои отзывы</h2>}

        {!isStaff && reviewsError && <div className="alert error" style={{ marginBottom: 16 }}>{reviewsError}</div>}

        {!isStaff && <section className="ticket-list">
          {myReviews.length === 0 && !reviewsError && (
            <div className="profile-empty">
              <Star size={40} />
              <p>Отзывов пока нет. Посмотрите фильм и поделитесь мнением.</p>
            </div>
          )}

          {myReviews.map((review) => (
            <article className="my-review-card" key={review.id}>
              <div className="my-review-header">
                <div className="my-review-title-row">
                  <span className="my-review-movie">{review.movie_title}</span>
                  <span className="review-score-badge">
                    <Star size={11} fill="currentColor" /> {review.score}/10
                  </span>
                </div>
                <Link to={`/movies/${review.movie_id}`} className="secondary-btn small">
                  К фильму
                </Link>
              </div>

              {review.text && <p className="review-text" style={{ marginBottom: 10 }}>{review.text}</p>}

              <div className="my-review-reactions">
                <span className={`reaction-count${review.likes > 0 ? " like" : ""}`}>
                  <ThumbsUp size={13} /> {review.likes}
                </span>
                <span className={`reaction-count${review.dislikes > 0 ? " dislike" : ""}`}>
                  <ThumbsDown size={13} /> {review.dislikes}
                </span>
              </div>
            </article>
          ))}
        </section>}

      </main>
    </>
  );
}
