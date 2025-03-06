from dataclasses import dataclass

from app.exceptions.users import UserAlreadyExistsError
from app.schemas.users import (
    CreateUserSchema,
    ReadUserSchema,
    RegisterUserSchema,
)
from app.services.auth import AbstractAuthService
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


@dataclass
class RegisterUserUseCase:
    auth_service: AbstractAuthService
    user_service: AbstractUserService
    token_service: AbstractJWTTokenService

    async def execute(
        self,
        user_in: RegisterUserSchema,
        uow: AbstractUnitOfWork,
    ) -> ReadUserSchema:

        user = await self.user_service.get_user_by_username(
            uow=uow,
            username=user_in.username,
        )

        if user is not None:
            raise UserAlreadyExistsError()

        user_auth_in = CreateUserSchema(
            **user_in.model_dump(exclude={"password"}),
            hashed_password=await self.token_service.hash_password(
                user_in.password,
            ),
        )
        return await self.auth_service.register(
            uow,
            user_auth_in,
        )
