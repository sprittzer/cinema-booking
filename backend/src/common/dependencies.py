from collections.abc import Callable
from typing import Annotated, Any

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.identity.models import User
from .security import decode_token

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


@inject
async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_security)],
    session: FromDishka[AsyncSession],
) -> User | None:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user if (user and user.is_active) else None


@inject
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: FromDishka[AsyncSession],
) -> User:
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен") from None

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    return user


CurrentUser = Annotated[object, Depends(get_current_user)]


def require_roles(*roles: str) -> Callable[..., Any]:
    async def dependency(user: Any = Depends(get_current_user)) -> Any:
        if user.role.value not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
        return user

    return dependency
