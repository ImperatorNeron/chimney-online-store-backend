from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.schemas.users import ReadUserSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUserService(ABC):

    @abstractmethod
    async def get_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> BaseModel: ...

    @abstractmethod
    async def get_user_by_id(
        self,
        uow: AbstractUnitOfWork,
        id: int,  # noqa
    ) -> BaseModel: ...


class UserService(AbstractUserService):

    async def get_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> ReadUserSchema:
        async with uow:
            return await uow.users.get_or_none(username=username)

    async def get_user_by_id(
        self,
        uow: AbstractUnitOfWork,
        id: int,  # noqa
    ) -> ReadUserSchema:
        async with uow:
            return await uow.users.get(id=id)
