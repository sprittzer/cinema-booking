import { useEffect, useMemo, useRef, useState } from "react";
import { ChevronRight, Search, Star } from "lucide-react";
import Header from "../components/Header";
import MovieCard from "../components/MovieCard";
import { getMovieImages, getMovies } from "../api/api";
import { Link } from "react-router-dom";


function YearSelect({ years, value, onChange }) {
  if (years.length === 0) return null;
  return (
    <div className="filter-group">
      <select className="filter-select" value={value || ""} onChange={(e) => onChange(e.target.value ? Number(e.target.value) : 0)}>
        <option value="">Все года</option>
        {[...years].sort((a, b) => b - a).map((y) => (
          <option key={y} value={y}>{y}</option>
        ))}
      </select>
      {value > 0 && <button type="button" className="filter-clear" onClick={() => onChange(0)}>×</button>}
    </div>
  );
}

function pluralMovies(n) {
  const abs = Math.abs(n) % 100;
  const r = abs % 10;
  if (abs > 10 && abs < 20) return `${n} фильмов`;
  if (r === 1) return `${n} фильм`;
  if (r >= 2 && r <= 4) return `${n} фильма`;
  return `${n} фильмов`;
}

export default function AfishaPage() {
  const [movies, setMovies] = useState([]);
  const [comingSoon, setComingSoon] = useState([]);
  const [activeGenre, setActiveGenre] = useState("");
  const [activeYear, setActiveYear] = useState(0);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [heroIndex, setHeroIndex] = useState(0);
  const [heroBackdrops, setHeroBackdrops] = useState({});
  const timerRef = useRef(null);

  useEffect(() => {
    getMovies({ status: "now_playing" })
      .then(setMovies)
      .catch(() => setError("Не удалось загрузить афишу"));
    getMovies({ status: "coming_soon" })
      .then(setComingSoon)
      .catch(() => {});
  }, []);

  const featuredMovies = useMemo(() => {
    const f = movies.filter((m) => m.is_featured);
    return f.length > 0 ? f : movies.slice(0, 1);
  }, [movies]);

  useEffect(() => {
    featuredMovies.forEach((m) => {
      getMovieImages(m.id).then((imgs) => {
        setHeroBackdrops((prev) => {
          if (prev[m.id] !== undefined) return prev;
          return { ...prev, [m.id]: imgs[0] || null };
        });
      });
    });
  }, [featuredMovies]);

  useEffect(() => {
    if (featuredMovies.length <= 1) return;
    timerRef.current = setInterval(
      () => setHeroIndex((p) => (p + 1) % featuredMovies.length),
      6000
    );
    return () => clearInterval(timerRef.current);
  }, [featuredMovies.length]);

  const goHero = (i) => {
    setHeroIndex(i);
    clearInterval(timerRef.current);
    if (featuredMovies.length > 1) {
      timerRef.current = setInterval(
        () => setHeroIndex((p) => (p + 1) % featuredMovies.length),
        6000
      );
    }
  };

  const featured = featuredMovies[heroIndex] || null;

  const genres = useMemo(() => {
    const all = movies.map((m) => m.genre).filter(Boolean);
    return [...new Set(all)].sort();
  }, [movies]);

  const years = useMemo(() => {
    const all = movies.map((m) => m.releaseYear).filter(Boolean);
    return [...new Set(all)].sort((a, b) => b - a);
  }, [movies]);

  const filtered = useMemo(() => {
    return movies.filter((movie) => {
      const byGenre = !activeGenre || movie.genre === activeGenre;
      const bySearch = movie.title.toLowerCase().includes(search.toLowerCase());
const byYear = !activeYear || movie.releaseYear === activeYear;
      return byGenre && bySearch && byYear;
    });
  }, [movies, activeGenre, search, activeYear]);

  return (
    <>
      <Header />

      <main className="app-page">
        <section className="hero">
          {featuredMovies.map((m, i) => (
            <div
              key={m.id}
              className={`hero-bg-slide${i === heroIndex ? " active" : ""}`}
              style={{ backgroundImage: heroBackdrops[m.id] ? `url(${heroBackdrops[m.id]})` : undefined }}
            />
          ))}
          <div className="hero-overlay" />

          <div className="hero-content">
            <span className="overline">Сейчас в прокате</span>
            <h1>{featured?.title || "Добро пожаловать в НеКино"}</h1>

            <div className="hero-meta">
              {featured && (
                <span className="hero-chip hero-chip-gold">
                  <Star size={14} fill="currentColor" />
                  <span data-tooltip="TMDB">{featured.tmdbRating != null ? featured.tmdbRating.toFixed(1) : "—"}</span>
                  <span className="rating-sep">/</span>
                  <span data-tooltip="Зрители">{featured.rating != null ? featured.rating.toFixed(1) : "—"}</span>
                </span>
              )}
              {featured?.genre && <span className="hero-chip">{featured.genre}</span>}
              {featured?.duration && <span className="hero-chip">{featured.duration} мин</span>}
              {featured?.ageLimit && <span className="hero-chip">{featured.ageLimit}</span>}
            </div>

            {featured && (
              <Link to={`/movies/${featured.id}`} className="primary-btn hero-btn">
                Подробнее <ChevronRight size={18} />
              </Link>
            )}
          </div>

          {featuredMovies.length > 1 && (
            <div className="hero-nav">
              <div className="slide-dots">
                {featuredMovies.map((_, i) => (
                  <button
                    key={i}
                    className={`slide-dot${i === heroIndex ? " active" : ""}`}
                    onClick={() => goHero(i)}
                  />
                ))}
              </div>
            </div>
          )}
        </section>

        <section className="content-shell">
          <div className="filters-row">
            <div className="search-box">
              <Search size={20} />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Поиск фильма..."
              />
            </div>

            <select className="filter-select" value={activeGenre} onChange={(e) => setActiveGenre(e.target.value)}>
              <option value="">Все жанры</option>
              {genres.map((g) => <option key={g} value={g}>{g}</option>)}
            </select>

            <YearSelect years={years} value={activeYear} onChange={setActiveYear} />
          </div>

          {comingSoon.length > 0 && (
            <section className="coming-soon-section">
              <div className="section-title">
                <h2>Скоро в кино</h2>
                <span>{comingSoon.length} фильм{comingSoon.length === 1 ? "" : comingSoon.length < 5 ? "а" : "ов"}</span>
              </div>
              <div className="movies-grid">
                {comingSoon.map((movie) => (
                  <MovieCard key={movie.id} movie={movie} badge="Скоро" />
                ))}
              </div>
            </section>
          )}

          <div className="section-title">
            <h2>Афиша</h2>
            <span>{pluralMovies(filtered.length)}</span>
          </div>

          {error && <div className="alert error">{error}</div>}

          <div className="movies-grid">
            {filtered.length === 0 ? (
              <p className="muted">Фильмы не найдены.</p>
            ) : (
              filtered.map((movie) => <MovieCard key={movie.id} movie={movie} />)
            )}
          </div>
        </section>
      </main>
    </>
  );
}
