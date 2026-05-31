import Seat from "./Seat";

export default function Hall({ seats, onSeatClick }) {
  const rows = seats.reduce((acc, seat) => {
    if (!acc[seat.row]) {
      acc[seat.row] = [];
    }

    acc[seat.row].push(seat);
    return acc;
  }, {});

  return (
    <div className="hall">
      <div className="screen">ЭКРАН</div>

      <div className="hall-rows">
        {Object.entries(rows).map(([rowNumber, rowSeats]) => (
          <div className="hall-row" key={rowNumber}>
            <span className="row-number">Ряд {rowNumber}</span>

            <div className="seats">
              {rowSeats.map((seat) => (
                <Seat
                  key={seat.id}
                  seat={seat}
                  onClick={onSeatClick}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="legend">
        <span>
          <b className="legend-box free"></b> Свободно
        </span>

        <span>
          <b className="legend-box booked"></b> Занято
        </span>
      </div>
    </div>
  );
}