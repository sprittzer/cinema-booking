from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from .config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, role: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=config.access_token_expire_minutes)
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, config.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict:
    return jwt.decode(token, config.secret_key, algorithms=["HS256"])
