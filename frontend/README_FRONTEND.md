# Frontend НеКино

Это новая frontend-часть проекта онлайн-кинотеатра.

## Логика

Без входа пользователь не может попасть на сайт. Все страницы, кроме `/login`, закрыты через `ProtectedRoute`.

Основные страницы:

- `/login` — вход и регистрация
- `/afisha` — афиша фильмов
- `/movies/:movieId` — выбор сеанса и мест
- `/profile` — личный кабинет пользователя

## Запуск

```bash
cd frontend
npm install
npm run dev
```

По умолчанию frontend обращается к backend:

```text
http://localhost:8000
```

Если backend на другом адресе, создай файл `.env`:

```text
VITE_API_URL=http://localhost:8000
```
