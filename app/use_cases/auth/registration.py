from dataclasses import dataclass

from app.core.exceptions.common import (
    EmailAlreadyExistsException,
    PhoneNumberAlreadyExistsException,
    UsernameAlreadyExistsException,
)
from app.schemas.users import CreateUserSchema, ReadUserSchema, RegisterUserSchema
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
        async with uow:
            user_by_username = await self.user_service.get_user_by_username(
                uow=uow, username=user_in.username,
            )

            if user_by_username:
                raise UsernameAlreadyExistsException()

            user_by_email = await self.user_service.get_user_by_email(
                uow=uow,
                email=user_in.email,
            )

            if user_by_email:
                raise EmailAlreadyExistsException()

            user_by_phone_number = await self.user_service.get_user_by_phone_number(
                uow=uow,
                phone_number=user_in.phone_number,
            )

            if user_by_phone_number:
                raise PhoneNumberAlreadyExistsException()

            return await self.auth_service.register(
                uow=uow,
                user_in=CreateUserSchema(
                    **user_in.model_dump(exclude={"password", "confirm_password"}),
                    hashed_password=self.token_service.hash_password(
                        user_in.password,
                    ),
                ),
            )
