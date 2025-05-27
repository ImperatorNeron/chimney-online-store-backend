import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions.common import EmailAlreadyExistsException, PhoneNumberAlreadyExistsException
from app.schemas.users import ReadUserSchema, UserUpdateSchema, UserUpdateWithPasswordSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


class AbstractUpdateUserUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_in: UserUpdateWithPasswordSchema,
        uow: AbstractUnitOfWork,
        user_id: int,
    ) -> ReadUserSchema: ...


@dataclass
class UpdateUserUseCase(AbstractUpdateUserUseCase):

    user_service: AbstractUserService
    token_service: AbstractJWTTokenService

    async def execute(
        self,
        user_in: UserUpdateWithPasswordSchema,
        uow: AbstractUnitOfWork,
        user_id: int,
    ) -> ReadUserSchema:
        logger.info(f"UpdateUserUseCase: update for user_id={user_id}")
        async with uow:

            update_data = user_in.model_dump(
                exclude={"password", "confirm_password"},
                exclude_unset=True,
            )
            if "email" in update_data:
                user_by_email = await self.user_service.get_user_by_email(
                    uow=uow,
                    email=user_in.email,
                )

                if user_by_email and user_by_email.id != user_id:
                    logger.warning(
                        f"Email '{user_in.email}' already used by another user",
                    )
                    raise EmailAlreadyExistsException()

            if "phone_number" in update_data:
                user_by_phone_number = await self.user_service.get_user_by_phone_number(
                    uow=uow,
                    phone_number=user_in.phone_number,
                )

                if user_by_phone_number and user_by_phone_number.id != user_id:
                    logger.warning(
                        f"Phone number '{user_in.phone_number}' already used by another user",
                    )
                    raise PhoneNumberAlreadyExistsException()

            if user_in.password is not None:
                hashed_password = self.token_service.hash_password(user_in.password)
                update_data["hashed_password"] = hashed_password
                logger.info(f"User {user_id} is changing password")

            new_user_data = await self.user_service.update_user(
                user_in=UserUpdateSchema(**update_data),
                user_id=user_id,
                uow=uow,
            )
            logger.info(
                f"User {user_id} successfully updated with fields: {list(update_data.keys())}",
            )
            return ReadUserSchema(
                **new_user_data.model_dump(exclude={"hashed_password"}),
            )
