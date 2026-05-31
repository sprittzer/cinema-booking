import { getToken, logout } from "../utils/storage";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- normalization ---

const GENRE_RU = {
  action: "Боевик",
  drama: "Драма",
  comedy: "Комедия",
  horror: "Ужасы",
  sci_fi: "Фантастика",
  thriller: "Триллер",
  romance: "Мелодрама",
  animation: "Анимация",
  documentary: "Документальный",
  other: "Другое",
};

function normalizeMovie(m) {
  return {
    ...m,
    duration: m.duration ?? m.duration_minutes,
    ageLimit: m.age_rating,
    posterUrl: m.poster_url,
    tmdbRating: m.tmdb_rating,
    rating: m.avg_rating,
    genre: GENRE_RU[m.genre] ?? m.genre,
    releaseYear: m.release_year ?? null,
  };
}

function normalizeSession(s) {
  const dt = s.start_time ? new Date(s.start_time) : null;
  return {
    ...s,
    movieId: s.movie_id,
    hallId: s.hall_id,
    date: dt ? dt.toLocaleDateString("ru-RU") : "",
    dateStr: dt ? dt.toLocaleDateString("sv") : "",
    time: dt ? dt.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }) : "",
    hall: s.hall_id,
  };
}

function normalizeSeat(s) {
  return {
    ...s,
    isBooked: s.is_booked ?? false,
  };
}

function normalizeBooking(b) {
  const dt = b.start_time ? new Date(b.start_time) : null;
  return {
    ...b,
    userId: b.user_id,
    sessionId: b.session_id,
    movieTitle: b.movie_title,
    sessionDate: dt ? dt.toLocaleDateString("ru-RU") : "",
    sessionTime: dt ? dt.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }) : "",
    seats: (b.seats || []).map(normalizeSeat),
  };
}

// --- http ---

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (response.status === 401) {
    logout();
    window.location.href = "/login";
    throw new Error("Сессия истекла");
  }

  if (!response.ok) {
    let message = "Ошибка запроса";
    try {
      const data = await response.json();
      message = data.detail || message;
    } catch {
      message = await response.text();
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

// --- auth ---

export async function login(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "Неверный email или пароль");
  }
  return response.json();
}

export async function register(name, email, password) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

export async function getMe() {
  return request("/users/me");
}

export async function updateMe(data) {
  return request("/users/me", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// --- users (admin) ---

export async function getUsers() {
  return request("/users");
}

export async function deleteUser(id) {
  return request(`/users/${id}`, { method: "DELETE" });
}

// --- movies ---

export async function getMovies(params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v != null))
  ).toString();
  const data = await request(`/movies${query ? `?${query}` : ""}`);
  return data.map(normalizeMovie);
}

export async function getMovieById(id) {
  return normalizeMovie(await request(`/movies/${id}`));
}

export async function createMovie(data) {
  const payload = {
    title: data.title,
    description: data.description,
    duration_minutes: data.duration ? Number(data.duration) : null,
    genre: data.genre || null,
    age_rating: data.age_limit || null,
    poster_url: data.poster_url || null,
    trailer_url: data.trailer_url || null,
    status: data.status || "now_playing",
  };
  return normalizeMovie(await request("/movies", { method: "POST", body: JSON.stringify(payload) }));
}

export async function updateMovie(id, data) {
  const payload = {
    title: data.title,
    description: data.description,
    duration_minutes: data.duration ? Number(data.duration) : undefined,
    genre: data.genre || undefined,
    age_rating: data.age_limit || undefined,
    poster_url: data.poster_url || undefined,
    trailer_url: data.trailer_url || undefined,
    status: data.status || undefined,
  };
  return normalizeMovie(await request(`/movies/${id}`, { method: "PUT", body: JSON.stringify(payload) }));
}

export async function deleteMovie(id) {
  return request(`/movies/${id}`, { method: "DELETE" });
}

// --- sessions ---

export async function getSessions(movieId) {
  const query = movieId ? `?movie_id=${movieId}` : "";
  const data = await request(`/sessions${query}`);
  return data.map(normalizeSession);
}

export async function getSessionById(id) {
  return normalizeSession(await request(`/sessions/${id}`));
}

export async function getSessionSeats(sessionId) {
  const session = await request(`/sessions/${sessionId}`);
  return (session.seats || []).map(normalizeSeat);
}

export async function createSession(data) {
  const start_time = `${data.date}T${data.time}:00`;
  const payload = {
    movie_id: Number(data.movie_id),
    hall_id: Number(data.hall_id),
    start_time,
    format: data.format || "2d",
    language: data.language || "ru",
    base_price: Number(data.base_price) || 500,
  };
  return normalizeSession(await request("/sessions", { method: "POST", body: JSON.stringify(payload) }));
}

export async function updateSession(id, data) {
  const start_time = data.date && data.time ? `${data.date}T${data.time}:00` : undefined;
  const payload = {
    ...(start_time ? { start_time } : {}),
    ...(data.movie_id ? { movie_id: Number(data.movie_id) } : {}),
    ...(data.hall_id ? { hall_id: Number(data.hall_id) } : {}),
    ...(data.format ? { format: data.format } : {}),
    ...(data.language ? { language: data.language } : {}),
    ...(data.base_price ? { base_price: Number(data.base_price) } : {}),
  };
  return normalizeSession(await request(`/sessions/${id}`, { method: "PUT", body: JSON.stringify(payload) }));
}

export async function cancelSession(id) {
  return request(`/sessions/${id}`, { method: "DELETE" });
}

// --- halls ---

export async function getHalls() {
  return request("/halls");
}

// --- bookings ---

export async function getMyBookings() {
  const data = await request("/bookings/me");
  return data.map(normalizeBooking);
}

export async function getBookings() {
  const data = await request("/bookings");
  return data.map(normalizeBooking);
}

export async function getSessionBookings(sessionId) {
  const data = await request(`/bookings/session/${sessionId}`);
  return data.map(normalizeBooking);
}

export async function createBooking(data) {
  const result = await request("/bookings", {
    method: "POST",
    body: JSON.stringify({
      session_id: data.sessionId,
      seat_ids: data.seatIds,
    }),
  });
  return normalizeBooking(result);
}

export async function payBooking(id) {
  return request(`/bookings/${id}/pay`, { method: "POST" });
}

export async function cancelBooking(id) {
  return request(`/bookings/${id}/cancel`, { method: "POST" });
}

export async function scanTicket(ticketCode) {
  return request("/tickets/scan", {
    method: "POST",
    body: JSON.stringify({ ticket_code: ticketCode }),
  });
}

export async function getMovieImages(movieId) {
  try {
    return await request(`/movies/${movieId}/images`);
  } catch {
    return [];
  }
}

// --- actors ---

export async function getMovieActors(movieId) {
  try {
    return await request(`/movies/${movieId}/actors`);
  } catch {
    return [];
  }
}

export async function getActors() {
  return request("/actors");
}

export async function createActor(data) {
  return request("/actors", { method: "POST", body: JSON.stringify(data) });
}

export async function updateActor(id, data) {
  return request(`/actors/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export async function deleteActor(id) {
  return request(`/actors/${id}`, { method: "DELETE" });
}

export async function addMovieActor(movieId, actorId, character = null) {
  return request(`/movies/${movieId}/actors`, {
    method: "POST",
    body: JSON.stringify({ actor_id: actorId, character }),
  });
}

export async function removeMovieActor(movieId, actorId) {
  return request(`/movies/${movieId}/actors/${actorId}`, { method: "DELETE" });
}

// --- reviews ---

export async function getMyReviews() {
  return request("/users/me/reviews");
}

export async function getReviews(movieId) {
  return request(`/movies/${movieId}/reviews`);
}

export async function createReview(movieId, data) {
  return request(`/movies/${movieId}/reviews`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteReview(movieId, reviewId) {
  return request(`/movies/${movieId}/reviews/${reviewId}`, { method: "DELETE" });
}

export async function reactToReview(movieId, reviewId, value) {
  return request(`/movies/${movieId}/reviews/${reviewId}/react`, {
    method: "POST",
    body: JSON.stringify({ value }),
  });
}

// --- api objects (обратная совместимость с существующими страницами) ---

export const usersApi = {
  getAll: getUsers,
  remove: deleteUser,
};

export const moviesApi = {
  getAll: getMovies,
  getById: getMovieById,
  create: createMovie,
  update: updateMovie,
  remove: deleteMovie,
};

export const sessionsApi = {
  getAll: getSessions,
  getById: getSessionById,
  create: createSession,
  update: updateSession,
  remove: cancelSession,
  getSeats: getSessionSeats,
};

export const bookingsApi = {
  getAll: getBookings,
  getMy: getMyBookings,
  getBySession: getSessionBookings,
  create: createBooking,
  pay: payBooking,
  cancel: cancelBooking,
};
