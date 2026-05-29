import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test_db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-tests")
os.environ.setdefault("TMDB_API_KEY", "test-tmdb-key")
os.environ.setdefault("RESEND_API_KEY", "test-resend-key")

from unittest.mock import AsyncMock

import pytest

from src.identity.models import Role, User
from src.scheduling.models import CinemaSession, SessionStatus


@pytest.fixture
def mock_user_dao():
    return AsyncMock()


@pytest.fixture
def mock_movie_dao():
    return AsyncMock()


@pytest.fixture
def mock_review_dao():
    return AsyncMock()


@pytest.fixture
def mock_booking_dao():
    return AsyncMock()


@pytest.fixture
def mock_session_db():
    return AsyncMock()


@pytest.fixture
def user() -> User:
    u = User()
    u.id = 1
    u.email = "test@example.com"
    u.password_hash = "$2b$12$placeholder"
    u.name = "Test User"
    u.role = Role.USER
    u.is_active = True
    return u


@pytest.fixture
def admin_user() -> User:
    u = User()
    u.id = 2
    u.email = "admin@example.com"
    u.name = "Admin"
    u.role = Role.ADMIN
    u.is_active = True
    return u


@pytest.fixture
def scheduled_session() -> CinemaSession:
    s = CinemaSession()
    s.id = 1
    s.movie_id = 1
    s.hall_id = 1
    s.base_price = 300.0
    s.status = SessionStatus.SCHEDULED
    return s
