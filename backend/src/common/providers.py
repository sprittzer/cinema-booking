from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .config import Config, config
from .db import async_session_factory


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return config


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as session:
            yield session
