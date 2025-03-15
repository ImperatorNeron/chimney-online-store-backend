from dataclasses import dataclass

from app.core.exceptions.common import InvalidCredentialsException
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

            return TokenInfoSchema(
                access_token=await self.token_service.create_access_token(
                    pk=user.id,
                    username=user.username,
                ),
                refresh_token=await self.token_service.create_refresh_token(
                    pk=user.id,
                ),
            )
