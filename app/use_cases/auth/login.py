import logging
from dataclasses import dataclass

from fastapi import Response

from app.core.exceptions.common import InvalidCredentialsException
from app.core.settings import settings
from app.schemas.tokens import TokenInfoSchema
from app.schemas.users import LoginUserSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


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
        logger.info(f"Login attempt for user: {user_in.username}")
        async with uow:
            user = await self.user_service.get_user_by_username(uow, user_in.username)

            if not user:
                logger.warning(f"Login failed: user '{user_in.username}' not found")
                raise InvalidCredentialsException()

            if not self.token_service.validate_password(
                user_in.password,
                user.hashed_password,
            ):
                logger.warning(
                    f"Login failed: invalid password for user '{user_in.username}'",
                )
                raise InvalidCredentialsException()

            # TODO: add to settings
            response.set_cookie(
                key="refresh_token",
                value=await self.token_service.create_refresh_token(pk=user.id),
                max_age=settings.auth_jwt.refresh_token_expire_days * 24 * 60,
                secure=settings.session.session_secure,
                httponly=settings.session.session_httponly,
                samesite=settings.session.same_site,
            )

            access_token = await self.token_service.create_access_token(
                pk=user.id,
                username=user.username,
            )
            logger.info(f"Login successful for user '{user.username}'")
            return TokenInfoSchema(access_token=access_token)
