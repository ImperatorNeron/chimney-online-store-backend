from abc import ABC, abstractmethod
from dataclasses import dataclass

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
            new_user_data = await self.user_service.update_user(
                user_in=user_in,
                user_id=user_id,
                uow=uow,
            )
            return ReadUserSchema(
                **new_user_data.model_dump(exclude={"hashed_password"}),
            )
