export default function Seat({ seat, onClick }) {
  const className = seat.isBooked ? "seat booked" : "seat free";

  return (
    <button
      className={className}
      disabled={seat.isBooked}
      onClick={() => onClick(seat)}
      title={`Ряд ${seat.row}, место ${seat.number}`}
    >
      {seat.number}
    </button>
  );
}