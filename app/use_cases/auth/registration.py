import logging
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


logger = logging.getLogger(__name__)


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

        logger.info(
            f"RegisterUserUseCase: start registration for username={user_in.username}, "
            f"email={user_in.email}, phone={user_in.phone_number}",
        )

        async with uow:

            update_data = user_in.model_dump(exclude_unset=True)

            user_by_username = await self.user_service.get_user_by_username(
                uow=uow,
                username=user_in.username,
            )

            if user_by_username:
                logger.warning(
                    f"Registration failed: username '{user_in.username}' already exists",
                )
                raise UsernameAlreadyExistsException(
                    meta={"username": user_in.username},
                )

            if "email" in update_data:
                user_by_email = await self.user_service.get_user_by_email(
                    uow=uow,
                    email=user_in.email,
                )
                if user_by_email:
                    logger.warning(
                        f"Registration failed: email '{user_in.email}' already exists",
                    )
                    raise EmailAlreadyExistsException(meta={"email": user_in.email})

            if "phone_number" in update_data:
                user_by_phone_number = await self.user_service.get_user_by_phone_number(
                    uow=uow,
                    phone_number=user_in.phone_number,
                )

                if user_by_phone_number:
                    logger.warning(
                        f"Registration failed: phone number '{user_in.phone_number}' already exists",
                    )
                    raise PhoneNumberAlreadyExistsException(
                        meta={"phone_number": user_in.phone_number},
                    )

            user = await self.auth_service.register(
                uow=uow,
                user_in=CreateUserSchema(
                    **user_in.model_dump(exclude={"password", "confirm_password"}),
                    hashed_password=self.token_service.hash_password(
                        user_in.password,
                    ),
                ),
            )

            logger.info(
                f"Registration successful: user_id={user.id}, username={user.username}, email={user.email}",
            )

            return user
