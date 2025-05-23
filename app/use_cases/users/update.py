from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions.common import EmailAlreadyExistsException, PhoneNumberAlreadyExistsException
from app.schemas.users import ReadUserSchema, UserUpdateSchema, UserUpdateWithPasswordSchema
from app.services.tokens import AbstractJWTTokenService
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


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
                    raise EmailAlreadyExistsException()

            if "phone_number" in update_data:
                user_by_phone_number = await self.user_service.get_user_by_phone_number(
                    uow=uow,
                    phone_number=user_in.phone_number,
                )

                if user_by_phone_number and user_by_phone_number.id != user_id:
                    raise PhoneNumberAlreadyExistsException()

            if user_in.password is not None:
                hashed_password = self.token_service.hash_password(user_in.password)
                update_data["hashed_password"] = hashed_password

            new_user_data = await self.user_service.update_user(
                user_in=UserUpdateSchema(**update_data),
                user_id=user_id,
                uow=uow,
            )

            return ReadUserSchema(
                **new_user_data.model_dump(exclude={"hashed_password"}),
            )
