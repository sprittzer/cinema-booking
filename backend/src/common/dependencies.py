from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, Any

from dishka.integrations.fastapi import FromDishka
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .security import decode_token

if TYPE_CHECKING:
    from src.identity.models import User

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: FromDishka[AsyncSession],
) -> "User":
    from src.identity.models import User

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
