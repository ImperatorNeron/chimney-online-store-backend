from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions.common import EmailAlreadyExistsException, PhoneNumberAlreadyExistsException
from app.schemas.users import ReadUserSchema, UserUpdateSchema
from app.services.users import AbstractUserService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUpdateUserUseCase(ABC):

    @abstractmethod
    async def execute(
        self,
        user_in: UserUpdateSchema,
        uow: AbstractUnitOfWork,
        user_id: int,
    ) -> ReadUserSchema: ...


@dataclass
class UpdateUserUseCase(AbstractUpdateUserUseCase):

    user_service: AbstractUserService

    async def execute(
        self,
        user_in: UserUpdateSchema,
        uow: AbstractUnitOfWork,
        user_id: int,
    ) -> ReadUserSchema:
        async with uow:

            user_by_email = await self.user_service.get_user_by_email(
                uow=uow,
                email=user_in.email,
            )

            if user_by_email and user_by_email.id != user_id:
                raise EmailAlreadyExistsException()

            user_by_phone_number = await self.user_service.get_user_by_phone_number(
                uow=uow,
                phone_number=user_in.phone_number,
            )

            if user_by_phone_number and user_by_phone_number.id != user_id:
                raise PhoneNumberAlreadyExistsException()

            new_user_data = await self.user_service.update_user(
                user_in=user_in,
                user_id=user_id,
                uow=uow,
            )

            return ReadUserSchema(
                **new_user_data.model_dump(exclude={"hashed_password"}),
            )
