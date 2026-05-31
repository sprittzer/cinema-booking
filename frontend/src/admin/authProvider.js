const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const authProvider = {
  login: async ({ username, password }) => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: username, password }),
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.detail || "Неверный email или пароль");
    }

    const { access_token } = await response.json();
    localStorage.setItem("admin_token", access_token);

    const meResponse = await fetch(`${API_URL}/users/me`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    const user = await meResponse.json();

    if (!["admin"].includes(user.role)) {
      localStorage.removeItem("admin_token");
      throw new Error("Недостаточно прав для входа в панель управления");
    }

    localStorage.setItem("admin_user", JSON.stringify(user));
  },

  logout: () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    return Promise.resolve();
  },

  checkAuth: () => {
    return localStorage.getItem("admin_token")
      ? Promise.resolve()
      : Promise.reject();
  },

  checkError: (error) => {
    if (error.status === 401 || error.status === 403) {
      localStorage.removeItem("admin_token");
      localStorage.removeItem("admin_user");
      return Promise.reject();
    }
    return Promise.resolve();
  },

  getPermissions: () => {
    const user = JSON.parse(localStorage.getItem("admin_user") || "{}");
    return Promise.resolve(user.role?.toLowerCase() || "");
  },

  getIdentity: () => {
    const user = JSON.parse(localStorage.getItem("admin_user") || "{}");
    return Promise.resolve({
      id: user.id,
      fullName: user.name,
      avatar: null,
    });
  },
};

export default authProvider;
