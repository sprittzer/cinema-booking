import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Hall from "../components/Hall";
import { createBooking, getSessionById, getSessionSeats } from "../api/api";
import { getCurrentUser } from "../utils/storage";
import { getTicketPrice, getPriceLabel } from "../utils/price";
import { formatSessionTime } from "../utils/date";

export default function BookingPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [session, setSession] = useState(null);
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const user = getCurrentUser();

  const ticketPrice = session ? getTicketPrice(session.time) : 0;
  const totalPrice = selectedSeats.length * ticketPrice;

  useEffect(() => {
    if (!user) {
      navigate("/login");
      return;
    }

    loadSession();
    loadSeats();
  }, [id]);

  async function loadSession() {
    try {
      const data = await getSessionById(id);
      setSession(data);
    } catch (err) {
      setError("Не удалось загрузить информацию о сеансе");
    }
  }

  async function loadSeats() {
    try {
      const data = await getSessionSeats(id);
      setSeats(data);
    } catch (err) {
      setError("Не удалось загрузить места");
    }
  }

  function handleSeatClick(seat) {
    if (seat.isBooked) {
      return;
    }

    const alreadyInOrder = selectedSeats.some(
      (selectedSeat) => selectedSeat.id === seat.id
    );

    if (alreadyInOrder) {
      setSelectedSeats(
        selectedSeats.filter((selectedSeat) => selectedSeat.id !== seat.id)
      );
    } else {
      setSelectedSeats([...selectedSeats, seat]);
    }

    setError("");
    setSuccess("");
  }

  async function handleBooking() {
    if (selectedSeats.length === 0) {
      setError("Выберите хотя бы одно место");
      return;
    }

    try {
      await createBooking({
        userId: user.id,
        sessionId: Number(id),
        seatIds: selectedSeats.map((seat) => seat.id),
        ticketPrice: ticketPrice,
        totalPrice: totalPrice,
      });

      setSuccess("Бронирование успешно создано");
      setError("");
      setSelectedSeats([]);

      await loadSeats();
    } catch (err) {
      setError("Не удалось забронировать места");
      setSuccess("");
    }
  }

  if (!session) {
    return (
      <section className="booking-page">
        <h1>Загрузка сеанса...</h1>
      </section>
    );
  }

  return (
    <section className="booking-page">
      <div className="page-title">
        <h1>Выбор мест</h1>

        <p>
          Сеанс: {formatSessionTime(session.time, session.date)}, зал{" "}
          {session.hall || 1}
        </p>
      </div>

      {error && <p className="error">{error}</p>}
      {success && <p className="success">{success}</p>}

      <div className="booking-layout">
        <Hall
          seats={seats}
          selectedSeats={selectedSeats}
          onSeatClick={handleSeatClick}
        />

        <aside className="booking-panel">
          <h2>Ваш заказ</h2>

          <p>
            Зал {session.hall || 1} ·{" "}
            {formatSessionTime(session.time, session.date)}
          </p>

          <p>
            <b>Тариф:</b> {getPriceLabel(session.time)}
          </p>

          <p>
            <b>Цена за билет:</b> {ticketPrice} ₽
          </p>

          {selectedSeats.length === 0 ? (
            <p className="muted">Места пока не выбраны.</p>
          ) : (
            <>
              <p>
                <b>Места:</b>
              </p>

              <ul className="selected-seats-list">
                {selectedSeats.map((seat) => (
                  <li key={seat.id}>
                    Ряд {seat.row}, место {seat.number}
                  </li>
                ))}
              </ul>

              <p className="total-price">
                <b>Итого:</b> {totalPrice} ₽
              </p>
            </>
          )}

          <button className="btn full" onClick={handleBooking}>
            Забронировать
          </button>
        </aside>
      </div>
    </section>
  );
}