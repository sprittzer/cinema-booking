import { useEffect, useMemo, useState } from "react";
import { Film, RefreshCcw, Shield, Ticket, Trash2 } from "lucide-react";
import Header from "../components/Header";
import { bookingsApi, moviesApi, sessionsApi, usersApi, getHalls } from "../api/api";
import { formatSessionTime } from "../utils/date";
import { roleLabel } from "../utils/storage";

const emptyMovie = {
  title: "", genre: "", description: "", duration: "",
  age_limit: "", poster_url: "", trailer_url: "", status: "now_playing",
};

const emptySession = {
  movie_id: "", hall_id: "", date: "", time: "",
  format: "2d", language: "ru", base_price: "500",
};

export default function AdminPage() {
  const [users, setUsers] = useState([]);
  const [movies, setMovies] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [bookings, setBookings] = useState([]);
  const [halls, setHalls] = useState([]);

  const [movieForm, setMovieForm] = useState(emptyMovie);
  const [sessionForm, setSessionForm] = useState(emptySession);
  const [editingMovieId, setEditingMovieId] = useState(null);
  const [editingSessionId, setEditingSessionId] = useState(null);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const stats = useMemo(() => ({
    movies: movies.length,
    sessions: sessions.length,
    users: users.length,
    bookings: bookings.length,
  }), [movies, sessions, users, bookings]);

  async function load() {
    const [usersData, moviesData, sessionsData, bookingsData, hallsData] = await Promise.all([
      usersApi.getAll(),
      moviesApi.getAll(),
      sessionsApi.getAll(),
      bookingsApi.getAll(),
      getHalls(),
    ]);
    setUsers(usersData);
    setMovies(moviesData);
    setSessions(sessionsData);
    setBookings(bookingsData);
    setHalls(hallsData);
  }

  useEffect(() => {
    load().catch((err) => setError(err.message || "Ошибка загрузки данных"));
  }, []);

  function changeMovieField(e) { setMovieForm({ ...movieForm, [e.target.name]: e.target.value }); }
  function changeSessionField(e) { setSessionForm({ ...sessionForm, [e.target.name]: e.target.value }); }

  function startEditMovie(movie) {
    setEditingMovieId(movie.id);
    setMovieForm({
      title: movie.title || "",
      genre: movie.genre || "",
      description: movie.description || "",
      duration: movie.duration || "",
      age_limit: movie.ageLimit || "",
      poster_url: movie.posterUrl || "",
      trailer_url: movie.trailer_url || "",
      status: movie.status || "now_playing",
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function cancelMovieEdit() { setEditingMovieId(null); setMovieForm(emptyMovie); }

  async function submitMovie(event) {
    event.preventDefault();
    setError(""); setMessage("");
    try {
      if (editingMovieId) {
        await moviesApi.update(editingMovieId, movieForm);
        setMessage("Фильм обновлён");
      } else {
        await moviesApi.create(movieForm);
        setMessage("Фильм добавлен");
      }
      cancelMovieEdit();
      await load();
    } catch (err) {
      setError(err.message || "Не удалось сохранить фильм");
    }
  }

  async function removeMovie(id) {
    if (!confirm("Удалить фильм? Вместе с ним удалятся связанные сеансы.")) return;
    try {
      await moviesApi.remove(id);
      setMessage("Фильм удалён");
      await load();
    } catch (err) {
      setError(err.message || "Не удалось удалить фильм");
    }
  }

  function startEditSession(session) {
    setEditingSessionId(session.id);
    const dt = session.start_time ? new Date(session.start_time) : null;
    setSessionForm({
      movie_id: session.movie_id || "",
      hall_id: session.hall_id || "",
      date: dt ? dt.toISOString().slice(0, 10) : "",
      time: dt ? dt.toTimeString().slice(0, 5) : "",
      format: session.format || "2d",
      language: session.language || "ru",
      base_price: session.base_price || "500",
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function cancelSessionEdit() { setEditingSessionId(null); setSessionForm(emptySession); }

  async function submitSession(event) {
    event.preventDefault();
    setError(""); setMessage("");
    try {
      if (editingSessionId) {
        await sessionsApi.update(editingSessionId, sessionForm);
        setMessage("Сеанс обновлён");
      } else {
        await sessionsApi.create(sessionForm);
        setMessage("Сеанс добавлен");
      }
      cancelSessionEdit();
      await load();
    } catch (err) {
      setError(err.message || "Не удалось сохранить сеанс");
    }
  }

  async function removeSession(id) {
    if (!confirm("Отменить сеанс?")) return;
    try {
      await sessionsApi.remove(id);
      setMessage("Сеанс отменён");
      await load();
    } catch (err) {
      setError(err.message || "Не удалось отменить сеанс");
    }
  }

  async function removeUser(id) {
    if (!confirm("Удалить пользователя?")) return;
    try {
      await usersApi.remove(id);
      setMessage("Пользователь удалён");
      await load();
    } catch (err) {
      setError(err.message || "Не удалось удалить пользователя");
    }
  }

  async function cancelBooking(id) {
    if (!confirm("Отменить бронирование?")) return;
    try {
      await bookingsApi.cancel(id);
      setMessage("Бронирование отменено");
      await load();
    } catch (err) {
      setError(err.message || "Не удалось отменить бронирование");
    }
  }

  return (
    <>
      <Header />
      <main className="admin-page">
        <div className="page-title">
          <span className="overline">Панель управления</span>
          <h1>Админ-панель</h1>
          <p>Управление фильмами, сеансами, пользователями и бронированиями.</p>
        </div>

        {error && <div className="alert error">{error}</div>}
        {message && <div className="alert success">{message}</div>}

        <section className="admin-stats">
          <div className="stat-card"><Film /><b>{stats.movies}</b><span>Фильмов</span></div>
          <div className="stat-card"><Ticket /><b>{stats.sessions}</b><span>Сеансов</span></div>
          <div className="stat-card"><Shield /><b>{stats.users}</b><span>Пользователей</span></div>
          <div className="stat-card"><RefreshCcw /><b>{stats.bookings}</b><span>Бронирований</span></div>
        </section>

        <section className="admin-grid-two">
          <div className="admin-card">
            <h2>{editingMovieId ? "Редактировать фильм" : "Добавить фильм"}</h2>
            <form onSubmit={submitMovie} className="admin-form">
              <input className="input" name="title" placeholder="Название" value={movieForm.title} onChange={changeMovieField} required />
              <select className="input" name="genre" value={movieForm.genre} onChange={changeMovieField}>
                <option value="">Жанр</option>
                {["action","drama","comedy","horror","sci_fi","thriller","romance","animation","documentary","other"].map(g => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
              <textarea className="input" name="description" placeholder="Описание" value={movieForm.description} onChange={changeMovieField} />
              <input className="input" name="duration" type="number" placeholder="Длительность, мин" value={movieForm.duration} onChange={changeMovieField} />
              <select className="input" name="age_limit" value={movieForm.age_limit} onChange={changeMovieField}>
                <option value="">Возрастное ограничение</option>
                {["0+","6+","12+","16+","18+"].map(r => <option key={r} value={r}>{r}</option>)}
              </select>
              <input className="input" name="poster_url" placeholder="URL постера" value={movieForm.poster_url} onChange={changeMovieField} />
              <input className="input" name="trailer_url" placeholder="URL трейлера (YouTube)" value={movieForm.trailer_url} onChange={changeMovieField} />
              <select className="input" name="status" value={movieForm.status} onChange={changeMovieField}>
                <option value="now_playing">Сейчас в прокате</option>
                <option value="coming_soon">Скоро</option>
                <option value="archived">Архив</option>
              </select>
              <div className="form-actions">
                <button className="primary-btn" type="submit">{editingMovieId ? "Сохранить" : "Добавить"}</button>
                {editingMovieId && <button className="secondary-btn" type="button" onClick={cancelMovieEdit}>Отмена</button>}
              </div>
            </form>
          </div>

          <div className="admin-card">
            <h2>{editingSessionId ? "Редактировать сеанс" : "Добавить сеанс"}</h2>
            <form onSubmit={submitSession} className="admin-form">
              <select className="input" name="movie_id" value={sessionForm.movie_id} onChange={changeSessionField} required>
                <option value="">Выберите фильм</option>
                {movies.map((m) => <option key={m.id} value={m.id}>{m.title}</option>)}
              </select>
              <select className="input" name="hall_id" value={sessionForm.hall_id} onChange={changeSessionField} required>
                <option value="">Выберите зал</option>
                {halls.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
              </select>
              <input className="input" name="date" type="date" value={sessionForm.date} onChange={changeSessionField} required />
              <input className="input" name="time" type="time" value={sessionForm.time} onChange={changeSessionField} required />
              <select className="input" name="format" value={sessionForm.format} onChange={changeSessionField}>
                <option value="2d">2D</option>
                <option value="3d">3D</option>
                <option value="imax">IMAX</option>
              </select>
              <select className="input" name="language" value={sessionForm.language} onChange={changeSessionField}>
                <option value="ru">Русский</option>
                <option value="en">Английский</option>
                <option value="en_sub">Английский (субтитры)</option>
              </select>
              <input className="input" name="base_price" type="number" placeholder="Базовая цена, ₽" value={sessionForm.base_price} onChange={changeSessionField} required />
              <div className="form-actions">
                <button className="primary-btn" type="submit">{editingSessionId ? "Сохранить" : "Добавить"}</button>
                {editingSessionId && <button className="secondary-btn" type="button" onClick={cancelSessionEdit}>Отмена</button>}
              </div>
            </form>
          </div>
        </section>

        <section className="admin-section">
          <h2>Фильмы</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Название</th><th>Жанр</th><th>Статус</th><th>Рейтинг</th><th>Действия</th></tr></thead>
              <tbody>
                {movies.map((movie) => (
                  <tr key={movie.id}>
                    <td>{movie.id}</td><td>{movie.title}</td><td>{movie.genre}</td>
                    <td>{movie.status}</td><td>{movie.rating ? movie.rating.toFixed(1) : "—"}</td>
                    <td className="actions-cell">
                      <button className="secondary-btn small" onClick={() => startEditMovie(movie)}>Изменить</button>
                      <button className="danger-btn small" onClick={() => removeMovie(movie.id)}><Trash2 size={14} /> Удалить</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <h2>Сеансы</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Фильм</th><th>Дата и время</th><th>Зал</th><th>Формат</th><th>Цена</th><th>Статус</th><th>Действия</th></tr></thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td>{session.id}</td>
                    <td>{session.movieTitle || `Фильм ${session.movie_id}`}</td>
                    <td>{formatSessionTime(session.time, session.date)}</td>
                    <td>{session.hall}</td>
                    <td>{session.format?.toUpperCase()}</td>
                    <td>{session.base_price} ₽</td>
                    <td>{session.status}</td>
                    <td className="actions-cell">
                      <button className="secondary-btn small" onClick={() => startEditSession(session)}>Изменить</button>
                      <button className="danger-btn small" onClick={() => removeSession(session.id)}><Trash2 size={14} /> Отменить</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <h2>Пользователи</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Имя</th><th>Email</th><th>Роль</th><th>Действия</th></tr></thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td><td>{user.name}</td><td>{user.email}</td>
                    <td>{roleLabel(user.role)}</td>
                    <td className="actions-cell">
                      <button className="danger-btn small" onClick={() => removeUser(user.id)}><Trash2 size={14} /> Удалить</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <h2>Все бронирования</h2>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Фильм</th><th>Сеанс</th><th>Места</th><th>Сумма</th><th>Статус</th><th>Действия</th></tr></thead>
              <tbody>
                {bookings.map((booking) => (
                  <tr key={booking.id}>
                    <td>{booking.id}</td>
                    <td>{booking.movieTitle}</td>
                    <td>{formatSessionTime(booking.sessionTime, booking.sessionDate)}</td>
                    <td>{(booking.seats || []).map((s) => `${String.fromCharCode(64 + s.row)}-${s.number}`).join(", ")}</td>
                    <td>{booking.total_price} ₽</td>
                    <td>{booking.status}</td>
                    <td className="actions-cell">
                      <button className="danger-btn small" onClick={() => cancelBooking(booking.id)}><Trash2 size={14} /> Отменить</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </>
  );
}
