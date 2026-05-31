export default function BookingCard({ booking }) {
  return (
    <div className="booking-card">
      <h3>{booking.movie_title || "Фильм"}</h3>
      <p><b>Дата:</b> {booking.session_date}</p>
      <p><b>Время:</b> {booking.session_time}</p>
      <p><b>Места:</b> {booking.seats.map((s) => `ряд ${s.row}, место ${s.number}`).join("; ")}</p>
      <p><b>Статус:</b> {booking.status}</p>
    </div>
  );
}
