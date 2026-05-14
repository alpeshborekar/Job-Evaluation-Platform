import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import MagicMock, patch

from services.auth_service import AuthService
from utils.errors import AuthenticationError, ValidationError

svc = AuthService()


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = AuthService._hash_password("mysecret123")

        assert hashed != "mysecret123"
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = AuthService._hash_password("mysecret123")

        assert AuthService._verify_password(
            "mysecret123",
            hashed,
        ) is True

    def test_verify_wrong_password(self):
        hashed = AuthService._hash_password("mysecret123")

        assert AuthService._verify_password(
            "wrongpassword",
            hashed,
        ) is False

    def test_verify_invalid_hash_returns_false(self):
        assert AuthService._verify_password(
            "anything",
            "notahash",
        ) is False


class TestLogin:
    def _make_user(self, username="alice", password="password123"):
        user = MagicMock()

        user.id = 1
        user.username = username
        user.email = f"{username}@test.com"
        user.password = AuthService._hash_password(password)
        user.is_active = True
        user.created_at = None

        return user

    # Successful login flow
    @patch("services.auth_service.db_session")
    @patch("services.auth_service.UserRepository")
    def test_login_success(self, MockRepo, mock_session):
        user = self._make_user()

        instance = MockRepo.return_value
        instance.get_by_username.return_value = user

        mock_session.return_value.__enter__ = lambda s: MagicMock()
        mock_session.return_value.__exit__ = MagicMock(return_value=False)

        with patch("services.auth_service.db_session") as ctx:
            ctx.return_value.__enter__ = lambda s: MagicMock()
            ctx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("services.auth_service.UserRepository") as Repo:
                inst = Repo.return_value
                inst.get_by_username.return_value = user

                result = svc.login(
                    username="alice",
                    password="password123",
                )

                assert result["username"] == "alice"
                assert "password" not in result

    def test_login_wrong_password_raises(self):
        user = self._make_user()

        with patch("services.auth_service.db_session") as ctx:
            ctx.return_value.__enter__ = lambda s: MagicMock()
            ctx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("services.auth_service.UserRepository") as Repo:
                Repo.return_value.get_by_username.return_value = user

                with pytest.raises(AuthenticationError):
                    svc.login(
                        username="alice",
                        password="wrongpassword",
                    )

    def test_login_unknown_user_raises(self):
        with patch("services.auth_service.db_session") as ctx:
            ctx.return_value.__enter__ = lambda s: MagicMock()
            ctx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("services.auth_service.UserRepository") as Repo:
                Repo.return_value.get_by_username.return_value = None

                with pytest.raises(AuthenticationError):
                    svc.login(
                        username="ghost",
                        password="anything",
                    )

    # Block login for inactive accounts
    def test_inactive_user_raises(self):
        user = self._make_user()
        user.is_active = False

        with patch("services.auth_service.db_session") as ctx:
            ctx.return_value.__enter__ = lambda s: MagicMock()
            ctx.return_value.__exit__ = MagicMock(return_value=False)

            with patch("services.auth_service.UserRepository") as Repo:
                Repo.return_value.get_by_username.return_value = user

                with pytest.raises(
                    AuthenticationError,
                    match="deactivated",
                ):
                    svc.login(
                        username="alice",
                        password="password123",
                    )


class TestSerializer:
    def test_serialize_excludes_password(self):
        user = MagicMock()

        user.id = 5
        user.username = "bob"
        user.email = "bob@test.com"
        user.created_at = None

        result = AuthService._serialize(user)

        assert "password" not in result
        assert result["id"] == 5
        assert result["username"] == "bob"