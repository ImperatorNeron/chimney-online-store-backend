from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from app.core.settings import settings
from app.exceptions.users import UserWasNotFoundError
from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import ReadUserWithPasswordSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


@dataclass
class BaseAuthUseCase:
    user_service: AbstractUserService
    token_service: AbstractJWTTokenService

    async def _fetch_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> ReadUserWithPasswordSchema:
        user: ReadUserWithPasswordSchema = await self.user_service.get_user_by_username(
            uow=uow,
            username=username,
        )

        if not user:
            raise UserWasNotFoundError()

        return user

    def _is_valid_password(
        self,
        password: str,
        hashed_password: bytes,
    ) -> bool:
        return self.token_service.validate_password(
            password=password,
            hashed_password=hashed_password,
        )

    async def _generate_tokens_info(
        self,
        pk: int,
        username: str,
    ) -> TokenInfoSchema:

        return TokenInfoSchema(
            access_token=await self._generate_access_token(
                pk=pk,
                username=username,
            ),
            refresh_token=await self._generate_refresh_token(pk=pk),
        )

    async def _generate_refresh_token(
        self,
        pk: int,
    ) -> str:
        return await self._generate_jwt(
            token_data={"sub": pk},
            token_type="refresh",
            expire_timedelta=timedelta(
                days=settings.auth_jwt.refresh_token_expire_days,
            ),
        )

    async def _generate_access_token(
        self,
        pk: int,
        username: str,
    ) -> str:
        return await self._generate_jwt(
            token_data={"sub": pk, "username": username},
            token_type="access",
            expire_minutes=settings.auth_jwt.access_token_expire_minutes,
        )

    async def _generate_jwt(
        self,
        token_type: str,
        token_data: dict,
        expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: Optional[timedelta] = None,
    ) -> str:

        payload = {"token_type": token_type}
        payload.update(token_data)

        return await self.token_service.encode_jwt(
            payload=payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
        )
