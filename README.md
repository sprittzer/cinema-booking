# Cinema Booking

Система онлайн-бронирования билетов в кинотеатр. Курсовой проект.

## Стек

**Backend**
- Python 3.12, FastAPI, SQLAlchemy 2 (async), asyncpg
- PostgreSQL — основная база данных
- Alembic — миграции
- Dishka — dependency injection
- JWT — аутентификация
- Resend — отправка email с QR-кодом билета
- TMDB API — импорт информации о фильмах
- uv — управление зависимостями

**Инфраструктура**
- Docker + Docker Compose
- GitHub Actions — CI (линтер, типизация, тесты)

## Запуск

### Docker

```bash
cp backend/.env.example backend/.env
# заполнить backend/.env

docker compose up --build
```

Миграции применяются автоматически при старте контейнера.

### Локально

```bash
cd backend
cp .env.example .env
# заполнить .env

uv sync
uv run alembic upgrade head
uv run uvicorn src.main:app --reload
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `DATABASE_URL` | строка подключения к PostgreSQL |
| `SECRET_KEY` | секрет для подписи JWT |
| `TMDB_API_KEY` | ключ TMDB API |
| `RESEND_API_KEY` | ключ Resend API |
| `EMAIL_FROM` | адрес отправителя писем |

## API

После запуска документация доступна по адресу:

- Swagger UI — `http://localhost:8000/docs`
- ReDoc — `http://localhost:8000/redoc`
