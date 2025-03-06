from abc import (
    ABC,
    abstractmethod,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import bcrypt
import jwt

from app.core.settings import settings
from app.exceptions.auth import InvalidJWTTokenError


class AbstractJWTTokenService(ABC):

    @abstractmethod
    def encode_jwt(
        payload: dict,
        secret_key: str,
        algorithm: str,
        expire_minutes: int,
        expire_timedelta: timedelta | None = None,
    ) -> str: ...

    @abstractmethod
    def decode_jwt(
        token: str | bytes,
        public_key: str,
        algorithm: str,
    ) -> None: ...

    @abstractmethod
    def hash_password(
        password: str,
    ) -> bytes: ...

    @abstractmethod
    def validate_password(
        password: str,
        hashed_password: bytes,
    ) -> bool: ...


class JWTTokenService:

    @staticmethod
    def encode_jwt(
        payload: dict,
        secret_key: str = settings.auth_jwt.private_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)

        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)

        to_encode.update(iat=now)
        to_encode.update(exp=expire)
        return jwt.encode(to_encode, secret_key, algorithm)

    @staticmethod
    def decode_jwt(
        token: str | bytes,
        public_key: str = settings.auth_jwt.public_key_path.read_text(),
        algorithm: str = settings.auth_jwt.algorithm,
    ) -> None:
        try:
            payload = jwt.decode(token, public_key, [algorithm])
            return payload
        except jwt.InvalidTokenError as e:
            raise InvalidJWTTokenError(e)

    @staticmethod
    def hash_password(password: str) -> bytes:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, salt)

    @staticmethod
    def validate_password(
        password: str,
        hashed_password: bytes,
    ) -> bool:
        return bcrypt.checkpw(
            password=password.encode(),
            hashed_password=hashed_password,
        )
