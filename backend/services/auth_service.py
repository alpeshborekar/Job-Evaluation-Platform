
from __future__ import annotations

import bcrypt

from backend.utils.database import (
    db_session,
)

from backend.utils.errors import (
    AuthenticationError,
    ValidationError,
)

from backend.utils.logger import (
    get_logger,
)

from backend.repositories.user_repo import (
    UserRepository,
)

logger = get_logger(__name__)

_BCRYPT_ROUNDS = 12


class AuthService:

    def register(
        self,
        *,
        username: str,
        email: str,
        password: str,
    ) -> dict:
        hashed = self._hash_password(
            password
        )

        with db_session() as session:
            user = UserRepository(
                session
            ).create(
                username=username,
                email=email,
                hashed_password=hashed,
            )

            payload = self._serialize(
                user
            )

        logger.info(
            "User registered username=%s",
            username,
        )

        return payload

    def login(
        self,
        *,
        username: str,
        password: str,
    ) -> dict:
        with db_session() as session:
            user = UserRepository(
                session
            ).get_by_username(
                username
            )

            candidate_hash = (
                user.password
                if user
                else (
                    "$2b$12$"
                    "invalidhashfortimingprotection"
                )
            )

            match = (
                self._verify_password(
                    password,
                    candidate_hash,
                )
            )

            if not user or not match:
                logger.warning(
                    "Failed login attempt username=%s",
                    username,
                )

                raise AuthenticationError(
                    "Invalid username or password."
                )

            if not user.is_active:
                raise AuthenticationError(
                    "This account has been deactivated."
                )

            payload = self._serialize(
                user
            )

        logger.info(
            "User logged in username=%s id=%s",
            username,
            payload["id"],
        )

        return payload

    def change_password(
        self,
        user_id: int,
        *,
        old_password: str,
        new_password: str,
    ) -> None:

        if len(new_password) < 8:
            raise ValidationError(
                (
                    "New password must "
                    "be at least 8 characters."
                )
            )

        with db_session() as session:
            repo = UserRepository(
                session
            )

            user = repo.get_by_id(
                user_id
            )

            if not self._verify_password(
                old_password,
                user.password,
            ):
                raise AuthenticationError(
                    "Current password is incorrect."
                )

            repo.update_password(
                user_id,
                self._hash_password(
                    new_password
                ),
            )

        logger.info(
            "Password changed user_id=%s",
            user_id,
        )

    @staticmethod
    def _hash_password(
        plain: str,
    ) -> str:
        return bcrypt.hashpw(
            plain.encode("utf-8"),
            bcrypt.gensalt(
                rounds=_BCRYPT_ROUNDS
            ),
        ).decode("utf-8")

    @staticmethod
    def _verify_password(
        plain: str,
        hashed: str,
    ) -> bool:
        try:
            return bcrypt.checkpw(
                plain.encode("utf-8"),
                hashed.encode("utf-8"),
            )

        except Exception:
            return False

    @staticmethod
    def _serialize(user) -> dict:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": (
                user.created_at.isoformat()
                if user.created_at
                else None
            ),
        }