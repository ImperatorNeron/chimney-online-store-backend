from abc import (
    ABC,
    abstractmethod,
)

from pydantic import BaseModel

from app.schemas.users import (
    CreateUserSchema,
    ReadUserSchema,
)
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractAuthService(ABC):

    @abstractmethod
    async def register(
        self,
        uow: AbstractUnitOfWork,
        user_in: CreateUserSchema,
    ) -> BaseModel: ...


class AuthService(AbstractAuthService):

    async def register(
        self,
        uow: AbstractUnitOfWork,
        user_in: CreateUserSchema,
    ) -> ReadUserSchema:
        async with uow:
            return await uow.users.create(item_in=user_in)
