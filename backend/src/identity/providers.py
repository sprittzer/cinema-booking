from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .dao import UserDAO
from .use_case import DeleteUserUseCase, GetHistoryUseCase, GetUsersUseCase, LoginUseCase, RegisterUseCase, UpdateProfileUseCase


class IdentityProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_dao(self, session: AsyncSession) -> UserDAO:
        return UserDAO(session)

    @provide
    def get_register_use_case(self, dao: UserDAO) -> RegisterUseCase:
        return RegisterUseCase(dao)

    @provide
    def get_login_use_case(self, dao: UserDAO) -> LoginUseCase:
        return LoginUseCase(dao)

    @provide
    def get_users_use_case(self, dao: UserDAO) -> GetUsersUseCase:
        return GetUsersUseCase(dao)

    @provide
    def get_update_profile_use_case(self, dao: UserDAO) -> UpdateProfileUseCase:
        return UpdateProfileUseCase(dao)

    @provide
    def get_delete_user_use_case(self, dao: UserDAO) -> DeleteUserUseCase:
        return DeleteUserUseCase(dao)

    @provide
    def get_history_use_case(self, session: AsyncSession) -> GetHistoryUseCase:
        return GetHistoryUseCase(session)
