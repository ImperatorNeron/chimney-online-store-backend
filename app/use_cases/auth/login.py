from dataclasses import dataclass

from fastapi import Response

from app.core.exceptions.common import InvalidCredentialsException
from app.core.settings import settings
from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import LoginUserSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


@dataclass
class LoginUserUseCase:

    token_service: AbstractJWTTokenService
    user_service: AbstractUserService

    async def execute(
        self,
        response: Response,
        uow: AbstractUnitOfWork,
        user_in: LoginUserSchema,
    ) -> TokenInfoSchema:
        async with uow:
            user = await self.user_service.get_user_by_username(uow, user_in.username)

            if not user:
                raise InvalidCredentialsException()

            if not self.token_service.validate_password(
                user_in.password,
                user.hashed_password,
            ):
                raise InvalidCredentialsException()

            # TODO: add to settings
            response.set_cookie(
                key="refresh_token",
                value=await self.token_service.create_refresh_token(pk=user.id),
                max_age=settings.auth_jwt.refresh_token_expire_days * 24 * 60,
                httponly=True,
                secure=False,
                samesite="lax",
            )

            return TokenInfoSchema(
                access_token=await self.token_service.create_access_token(
                    pk=user.id,
                    username=user.username,
                ),
            )
