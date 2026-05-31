const ROW_NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"];

const SEAT_LABELS = {
  standard: "Стандарт",
  vip: "VIP",
  couple: "Диван",
};

export default function SeatMap({ seats, selectedSeats, onSeatClick }) {
  const byRow = seats.reduce((acc, seat) => {
    if (!acc[seat.row]) acc[seat.row] = [];
    acc[seat.row].push(seat);
    return acc;
  }, {});

  function seatClass(seat) {
    const type = seat.seat_type && seat.seat_type !== "standard" ? ` seat-${seat.seat_type}` : "";
    if (seat.is_active === false) return `seat unavailable${type}`;
    if (seat.isBooked) return `seat booked${type}`;
    const isSelected = selectedSeats.some((item) => item.id === seat.id);
    if (isSelected) return `seat selected${type}`;
    return `seat free${type}`;
  }

  function seatTooltip(seat) {
    const label = SEAT_LABELS[seat.seat_type] || "Место";
    const price = seat.price != null ? ` · ${seat.price} ₽` : "";
    if (seat.is_active === false) return `${label} · Недоступно`;
    if (seat.isBooked) return `${label} · Занято`;
    return `${label}${price}`;
  }

  const hasVip = seats.some((s) => s.seat_type === "vip");
  const hasCouple = seats.some((s) => s.seat_type === "couple");

  return (
    <div className="seatmap-card">
      <div className="screen-line"></div>
      <div className="screen-text">ЭКРАН</div>

      <div className="seatmap">
        {Object.entries(byRow).map(([row, rowSeats]) => (
          <div className="seat-row" key={row}>
            <span className="row-label">
              {ROW_NAMES[Number(row) - 1] || row}
            </span>

            <div className="seat-row-items">
              {rowSeats.map((seat) => (
                <button
                  key={seat.id}
                  className={seatClass(seat)}
                  onClick={() => onSeatClick(seat)}
                  disabled={seat.is_active === false || seat.isBooked}
                  data-tooltip={seatTooltip(seat)}
                >
                  {seat.is_active === false || seat.isBooked ? "✕" : seat.number}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="seat-legend">
        <span><i className="legend-dot free"></i>Стандарт</span>
        {hasVip && (
          <>
            <span className="legend-divider"></span>
            <span><i className="legend-dot free seat-vip"></i>VIP</span>
          </>
        )}
        {hasCouple && (
          <>
            <span className="legend-divider"></span>
            <span><i className="legend-dot free seat-couple"></i>Диван</span>
          </>
        )}
      </div>
    </div>
  );
}
