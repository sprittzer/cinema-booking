import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Ticket } from "lucide-react";

import Header from "../components/Header";
import SeatMap from "../components/SeatMap";

import { createBooking, getMovieById, getSessionSeats, getSessions, payBooking } from "../api/api";
import { getCurrentUser, hasRole } from "../utils/storage";

const ROW_NAMES = ["", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J"];
const WEEK_DAYS = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"];
const MONTHS = ["янв","фев","мар","апр","май","июн","июл","авг","сен","окт","ноя","дек"];

function formatDateChip(dateStr) {
  const today = new Date().toLocaleDateString("sv");
  const tomorrow = new Date(Date.now() + 86400000).toLocaleDateString("sv");
  if (dateStr === today) return "Сегодня";
  if (dateStr === tomorrow) return "Завтра";
  const [year, month, day] = dateStr.split("-").map(Number);
  const d = new Date(year, month - 1, day);
  return `${WEEK_DAYS[d.getDay()]} ${day} ${MONTHS[month - 1]}`;
}

export default function MovieBookingPage() {
  const { movieId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    if (hasRole(getCurrentUser(), ["admin"])) navigate("/afisha", { replace: true });
  }, []);

  const [movie, setMovie] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [activeDate, setActiveDate] = useState(null);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getMovieById(movieId), getSessions(movieId)])
      .then(([movieData, sessionData]) => {
        if (movieData.status === "coming_soon") {
          navigate(`/movies/${movieId}`, { replace: true });
          return;
        }
        setMovie(movieData);
        setSessions(sessionData);
        if (sessionData.length > 0) {
          const firstDate = [...new Set(sessionData.map((s) => s.dateStr))].sort()[0];
          const firstSession = sessionData.find((s) => s.dateStr === firstDate);
          setActiveDate(firstDate);
          setActiveSessionId(firstSession?.id ?? null);
        }
      })
      .catch(() => setError("Не удалось загрузить фильм"));
  }, [movieId]);

  useEffect(() => {
    if (!activeSessionId) return;
    setSelectedSeats([]);
    getSessionSeats(activeSessionId)
      .then(setSeats)
      .catch(() => setError("Не удалось загрузить места"));
  }, [activeSessionId]);

  const sessionsByDate = useMemo(() => {
    const map = {};
    sessions.forEach((s) => {
      if (!map[s.dateStr]) map[s.dateStr] = [];
      map[s.dateStr].push(s);
    });
    return map;
  }, [sessions]);

  const dates = useMemo(() => Object.keys(sessionsByDate).sort(), [sessionsByDate]);

  function selectDate(date) {
    if (date === activeDate) return;
    setActiveDate(date);
    const first = sessionsByDate[date]?.[0];
    setActiveSessionId(first?.id ?? null);
    setSeats([]);
    setSelectedSeats([]);
    setMessage("");
    setError("");
  }

  function selectSession(sessionId) {
    if (sessionId === activeSessionId) return;
    setActiveSessionId(sessionId);
    setSelectedSeats([]);
    setMessage("");
    setError("");
  }

  const activeSession = sessions.find((s) => s.id === activeSessionId);
  const totalPrice = selectedSeats.reduce((sum, seat) => sum + (seat.price || 0), 0);

  function toggleSeat(seat) {
    if (seat.isBooked) return;
    const exists = selectedSeats.some((s) => s.id === seat.id);
    setSelectedSeats(exists ? selectedSeats.filter((s) => s.id !== seat.id) : [...selectedSeats, seat]);
    setError("");
    setMessage("");
  }

  async function book() {
    if (!selectedSeats.length) { setError("Сначала выберите хотя бы одно место"); return; }
    setError("");
    setMessage("");
    try {
      const booking = await createBooking({ sessionId: activeSessionId, seatIds: selectedSeats.map((s) => s.id) });
      await payBooking(booking.id);
      setMessage("Оплата прошла успешно! Билет появился в личном кабинете.");
      setSelectedSeats([]);
      setSeats(await getSessionSeats(activeSessionId));
    } catch (err) {
      setError(err.message || "Не удалось оформить бронь");
    }
  }

  return (
    <>
      <Header />

      <main className="booking-page">
        <button className="back-btn" onClick={() => navigate(`/movies/${movieId}`)}>
          <ArrowLeft size={20} />
        </button>

        <section className="booking-head">
          <img src={movie?.posterUrl} alt={movie?.title || "Постер фильма"} />
          <div>
            <h1>{movie?.title}</h1>
            <p>{movie?.genre} · {movie?.duration || 120} мин · {movie?.ageLimit}</p>
          </div>
        </section>

        {error && <div className="alert error">{error}</div>}

        {sessions.length === 0 && movie ? (
          <section className="no-sessions-card">
            <h2>Доступных сеансов нет</h2>
            <p>Для этого фильма нет добавленных сеансов. Попробуйте позже.</p>
          </section>
        ) : sessions.length > 0 && (
          <section className="booking-session-picker">
            <h2 className="session-picker-title">Выбор сеанса</h2>

            <div className="date-chips">
              {dates.map((date) => (
                <button
                  key={date}
                  className={`date-chip${activeDate === date ? " active" : ""}`}
                  onClick={() => selectDate(date)}
                >
                  {formatDateChip(date)}
                </button>
              ))}
            </div>

            {activeDate && (
              <div className="time-chips">
                {sessionsByDate[activeDate].map((s) => (
                  <button
                    key={s.id}
                    className={`time-chip${activeSessionId === s.id ? " active" : ""}`}
                    onClick={() => selectSession(s.id)}
                  >
                    <span className="time-chip-time">{s.time}</span>
                    <span className="time-chip-hall">Зал {s.hall}</span>
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {activeSessionId && (
          <section className="booking-layout">
            <SeatMap seats={seats} selectedSeats={selectedSeats} onSeatClick={toggleSeat} />

            <aside className="order-card">
              <h2>Ваш заказ</h2>
              <p className="order-session-info">
                {formatDateChip(activeDate)} · {activeSession?.time} · Зал {activeSession?.hall}
              </p>
              {activeSession?.base_price && (
                <p className="order-base-price">Базовая цена: {activeSession.base_price} ₽</p>
              )}

              {selectedSeats.length === 0 ? (
                <div className="empty-order">
                  <Ticket size={36} />
                  <span>Нажмите на свободное место</span>
                </div>
              ) : (
                <>
                  <div className="chosen-seats">
                    {selectedSeats.map((seat) => (
                      <span key={seat.id}>
                        {ROW_NAMES[seat.row] || seat.row}-{seat.number}
                        {seat.seat_type !== "standard" && ` (${seat.seat_type})`}
                      </span>
                    ))}
                  </div>

                  <div className="total-row">
                    <span>Итого</span>
                    <b>{totalPrice} ₽</b>
                  </div>

                  <button className="primary-btn" onClick={book}>
                    Оплатить
                  </button>
                </>
              )}

              {message && <div className="alert success">{message}</div>}
            </aside>
          </section>
        )}
      </main>
    </>
  );
}
