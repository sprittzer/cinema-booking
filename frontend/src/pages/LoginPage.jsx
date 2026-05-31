import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Clapperboard } from "lucide-react";
import Logo from "../components/Logo";
import { login, register, getMe } from "../api/api";
import { saveToken, saveCurrentUser } from "../utils/storage";

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function changeField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      let token;

      if (mode === "login") {
        const data = await login(form.email, form.password);
        token = data.access_token;
      } else {
        const data = await register(form.name.trim(), form.email.trim(), form.password);
        token = data.access_token;
      }

      saveToken(token);
      const user = await getMe();
      saveCurrentUser(user);
      navigate("/afisha");
    } catch (err) {
      setError(err.message || "Ошибка входа");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <section className="login-quote">
        <h1>Кино — это жизнь в темноте.</h1>
        <p>— Роже Эберт</p>
      </section>

      <section className="login-panel">
        <Logo />

        <div className="login-card">
          <h2>{mode === "login" ? "Добро пожаловать" : "Создать аккаунт"}</h2>

          <form onSubmit={submit}>
            {mode === "register" && (
              <label>
                Имя
                <input name="name" value={form.name} onChange={changeField} required placeholder="Алексей" />
              </label>
            )}

            <label>
              Email
              <input name="email" type="email" value={form.email} onChange={changeField} required placeholder="Введите вашу почту" />
            </label>

            <label>
              Пароль
              <input name="password" type="password" value={form.password} onChange={changeField} required placeholder="Введите пароль" />
            </label>

            {error && <div className="alert error">{error}</div>}

            <button className="primary-btn" type="submit" disabled={loading}>
              {loading ? "Загрузка..." : mode === "login" ? "Войти" : "Зарегистрироваться"}
            </button>
          </form>

          <button className="switch-mode" onClick={() => setMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "Нет аккаунта? Зарегистрироваться" : "Уже есть аккаунт? Войти"}
          </button>
          
        </div>
      </section>
    </main>
  );
}
