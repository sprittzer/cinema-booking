import pytest

from src.common.exceptions import AlreadyExistsError, UnauthorizedError
from src.common.security import hash_password
from src.identity.models import User
from src.identity.scheme import LoginRequest, RegisterRequest
from src.identity.use_case import LoginUseCase, RegisterUseCase


class TestRegisterUseCase:
    async def test_register_success(self, mock_user_dao):
        mock_user_dao.get_by_email.return_value = None
        created_user = User()
        created_user.id = 1
        created_user.role = __import__("src.identity.models", fromlist=["Role"]).Role.USER
        mock_user_dao.create.return_value = created_user

        use_case = RegisterUseCase(mock_user_dao)
        result = await use_case.execute(
            RegisterRequest(email="test@example.com", password="password123", name="Test")
        )

        assert result.access_token
        assert result.token_type == "bearer"
        mock_user_dao.create.assert_called_once()

    async def test_register_duplicate_email(self, mock_user_dao, user):
        mock_user_dao.get_by_email.return_value = user

        use_case = RegisterUseCase(mock_user_dao)
        with pytest.raises(AlreadyExistsError):
            await use_case.execute(
                RegisterRequest(email="test@example.com", password="password123", name="Test")
            )


class TestLoginUseCase:
    async def test_login_success(self, mock_user_dao, user):
        user.password_hash = hash_password("password123")
        mock_user_dao.get_by_email.return_value = user

        use_case = LoginUseCase(mock_user_dao)
        result = await use_case.execute(
            LoginRequest(email="test@example.com", password="password123")
        )

        assert result.access_token

    async def test_login_wrong_password(self, mock_user_dao, user):
        user.password_hash = hash_password("correct_password")
        mock_user_dao.get_by_email.return_value = user

        use_case = LoginUseCase(mock_user_dao)
        with pytest.raises(UnauthorizedError):
            await use_case.execute(
                LoginRequest(email="test@example.com", password="wrong_password")
            )

    async def test_login_user_not_found(self, mock_user_dao):
        mock_user_dao.get_by_email.return_value = None

        use_case = LoginUseCase(mock_user_dao)
        with pytest.raises(UnauthorizedError):
            await use_case.execute(
                LoginRequest(email="nobody@example.com", password="password")
            )
