from __future__ import annotations

from sqlalchemy.orm import Session

from.models.orm import User

from.utils.errors import (
    NotFoundError,
    ConflictError,
)

from.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


class UserRepository:

    def __init__(
        self,
        session: Session,
    ):
        self._s = session

    def create(
        self,
        *,
        username: str,
        email: str,
        hashed_password: str,
    ) -> User:

        if self.exists_by_username(
            username
        ):
            raise ConflictError(
                (
                    f"Username '{username}' "
                    "is already taken."
                )
            )

        if self.exists_by_email(
            email
        ):
            raise ConflictError(
                (
                    f"Email '{email}' "
                    "is already registered."
                )
            )

        user = User(
            username=username,
            email=email,
            password=hashed_password,
        )

        self._s.add(user)

        self._s.flush()

        logger.info(
            "User created id=%s username=%s",
            user.id,
            username,
        )

        return user

    def update_password(
        self,
        user_id: int,
        new_hashed: str,
    ) -> None:

        user = self._get_or_raise(
            user_id
        )

        user.password = new_hashed

    def deactivate(
        self,
        user_id: int,
    ) -> None:

        user = self._get_or_raise(
            user_id
        )

        user.is_active = False

    def get_by_id(
        self,
        user_id: int,
    ) -> User:
        return self._get_or_raise(
            user_id
        )

    def get_by_username(
        self,
        username: str,
    ) -> User | None:

        return (
            self._s.query(User)
            .filter(
                User.username == username,
                User.is_active == True,
            )
            .first()
        )

    def get_by_email(
        self,
        email: str,
    ) -> User | None:

        return (
            self._s.query(User)
            .filter(
                User.email == email,
                User.is_active == True,
            )
            .first()
        )

    def exists_by_username(
        self,
        username: str,
    ) -> bool:

        return self._s.query(
            self._s.query(User)
            .filter(
                User.username == username
            )
            .exists()
        ).scalar()

    def exists_by_email(
        self,
        email: str,
    ) -> bool:

        return self._s.query(
            self._s.query(User)
            .filter(
                User.email == email
            )
            .exists()
        ).scalar()

    def _get_or_raise(
        self,
        user_id: int,
    ) -> User:

        user = self._s.get(
            User,
            user_id,
        )

        if not user:
            raise NotFoundError(
                f"User {user_id} not found."
            )

        return user