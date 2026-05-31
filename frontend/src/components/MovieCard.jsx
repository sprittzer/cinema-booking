import { Clock, Star } from "lucide-react";
import { Link } from "react-router-dom";

export default function MovieCard({ movie, sessions = [], badge = null }) {
  return (
    <Link to={`/movies/${movie.id}`} className="movie-card">
      <div className="movie-poster">
        <img src={movie.posterUrl || "/poster-fallback.jpg"} alt={movie.title} />
        {movie.ageLimit && (
          <span className={`age-badge age-${movie.ageLimit.replace("+", "")}`}>
            {movie.ageLimit}
          </span>
        )}
        {badge && <span className="poster-badge">{badge}</span>}
        <span className="rating">
          <Star size={14} fill="currentColor" />
          {movie.tmdbRating != null ? movie.tmdbRating.toFixed(1) : "—"}
          <span className="rating-sep">/</span>
          {movie.rating != null ? movie.rating.toFixed(1) : "—"}
        </span>
      </div>

      <h3>{movie.title}</h3>
      <p>{movie.genre} · {movie.duration || 120} мин</p>

      {sessions.length > 0 && (
        <div className="card-sessions">
          {sessions.slice(0, 5).map((s) => (
            <span key={s.id} className="card-session-chip">{s.time}</span>
          ))}
        </div>
      )}

      <span className="duration-line">
        <Clock size={14} /> {Math.floor((movie.duration || 120) / 60)} ч {(movie.duration || 120) % 60} мин
      </span>
    </Link>
  );
}
