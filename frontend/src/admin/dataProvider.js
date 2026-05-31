const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
  return localStorage.getItem("admin_token");
}

async function apiRequest(path, options = {}) {
  const token = getToken();
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw { status: response.status, message: data.detail || "Ошибка запроса" };
  }

  if (response.status === 204) return null;
  return response.json();
}

// маппинг react-admin resource → наши API-пути
const RESOURCE_MAP = {
  movies: "/movies",
  sessions: "/sessions",
  halls: "/halls",
  bookings: "/bookings",
  users: "/users",
};

function toPath(resource) {
  return RESOURCE_MAP[resource] || `/${resource}`;
}

// нормализация данных для отображения
function normalizeRecord(resource, record) {
  if (resource === "movies") {
    return {
      ...record,
      duration: record.duration_minutes,
      age_limit: record.age_rating,
      rating: record.avg_rating,
    };
  }
  if (resource === "sessions") {
    const dt = record.start_time ? new Date(record.start_time) : null;
    return {
      ...record,
      date: dt ? dt.toLocaleDateString("sv") : "",
      time: dt ? dt.toTimeString().slice(0, 5) : "",
    };
  }
  return record;
}

// нормализация данных при отправке на сервер
function denormalizeRecord(resource, data) {
  if (resource === "movies") {
    return {
      title: data.title,
      description: data.description,
      duration_minutes: data.duration ? Number(data.duration) : null,
      genre: data.genre || null,
      age_rating: data.age_limit || null,
      poster_url: data.poster_url || null,
      trailer_url: data.trailer_url || null,
      status: data.status || "now_playing",
      is_featured: data.is_featured || false,
    };
  }
  if (resource === "sessions") {
    const start_time =
      data.date && data.time
        ? new Date(`${data.date}T${data.time}:00`).toISOString()
        : data.start_time;
    return {
      movie_id: Number(data.movie_id),
      hall_id: Number(data.hall_id),
      start_time,
      format: data.format || "2d",
      language: data.language || "ru",
      base_price: Number(data.base_price) || 500,
    };
  }
  if (resource === "users") {
    // create: all fields; update: only role and is_active
    if (data.password !== undefined) {
      return { email: data.email, password: data.password, name: data.name, role: data.role || "user" };
    }
    return { role: data.role, is_active: data.is_active };
  }
  return data;
}

const dataProvider = {
  getList: async (resource, { pagination, sort, filter }) => {
    const params = new URLSearchParams();
    if (filter) {
      Object.entries(filter).forEach(([key, value]) => {
        if (value != null && value !== "") params.append(key, value);
      });
    }

    const data = await apiRequest(`${toPath(resource)}${params.toString() ? `?${params}` : ""}`);
    const list = Array.isArray(data) ? data : data.items || [];
    const normalized = list.map((r) => normalizeRecord(resource, r));

    // frontend pagination (сервер возвращает всё)
    const { page = 1, perPage = 25 } = pagination || {};
    const start = (page - 1) * perPage;
    const paginated = normalized.slice(start, start + perPage);

    return { data: paginated, total: normalized.length };
  },

  getOne: async (resource, { id }) => {
    const data = await apiRequest(`${toPath(resource)}/${id}`);
    return { data: normalizeRecord(resource, data) };
  },

  getMany: async (resource, { ids }) => {
    const data = await Promise.all(ids.map((id) => apiRequest(`${toPath(resource)}/${id}`)));
    return { data: data.map((r) => normalizeRecord(resource, r)) };
  },

  getManyReference: async (resource, { target, id }) => {
    const data = await apiRequest(`${toPath(resource)}?${target}=${id}`);
    const list = Array.isArray(data) ? data : [];
    return { data: list.map((r) => normalizeRecord(resource, r)), total: list.length };
  },

  create: async (resource, { data }) => {
    const payload = denormalizeRecord(resource, data);
    const result = await apiRequest(toPath(resource), {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return { data: normalizeRecord(resource, result) };
  },

  update: async (resource, { id, data }) => {
    const payload = denormalizeRecord(resource, data);
    const result = await apiRequest(`${toPath(resource)}/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    return { data: normalizeRecord(resource, result) };
  },

  delete: async (resource, { id }) => {
    if (resource === "sessions" || resource === "bookings") {
      await apiRequest(`${toPath(resource)}/${id}/cancel`, { method: "POST" }).catch(() =>
        apiRequest(`${toPath(resource)}/${id}`, { method: "DELETE" })
      );
    } else {
      await apiRequest(`${toPath(resource)}/${id}`, { method: "DELETE" });
    }
    return { data: { id } };
  },

  deleteMany: async (resource, { ids }) => {
    await Promise.all(ids.map((id) => dataProvider.delete(resource, { id })));
    return { data: ids };
  },
};

export default dataProvider;
