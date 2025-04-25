from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.schemas.users import ReadUserSchema, ReadUserWithPasswordSchema, UserUpdateSchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUserService(ABC):

    @abstractmethod
    async def get_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> BaseModel: ...

    @abstractmethod
    async def get_user_by_email(
        self,
        uow: AbstractUnitOfWork,
        email: str,
    ) -> BaseModel: ...

    @abstractmethod
    async def get_user_by_phone_number(
        self,
        uow: AbstractUnitOfWork,
        phone_number: str,
    ) -> BaseModel: ...

    @abstractmethod
    async def get_user_by_id(
        self,
        uow: AbstractUnitOfWork,
        id: int,  # noqa
    ) -> BaseModel: ...

    @abstractmethod
    async def update_user(
        self,
        user_in: UserUpdateSchema,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> BaseModel: ...


class UserService(AbstractUserService):

    async def get_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> ReadUserSchema:
        return await uow.users.get_or_none(username=username)

    async def get_user_by_email(
        self,
        uow: AbstractUnitOfWork,
        email: str,
    ) -> ReadUserSchema:
        return await uow.users.get_or_none(email=email)

    async def get_user_by_phone_number(
        self,
        uow: AbstractUnitOfWork,
        phone_number: str,
    ) -> ReadUserSchema:
        return await uow.users.get_or_none(phone_number=phone_number)

    async def get_user_by_id(
        self,
        uow: AbstractUnitOfWork,
        id: int,  # noqa
    ) -> ReadUserSchema:
        async with uow:
            return await uow.users.get(id=id)

    async def update_user(
        self,
        user_in: UserUpdateSchema,
        user_id: int,
        uow: AbstractUnitOfWork,
    ) -> ReadUserWithPasswordSchema:
        return await uow.users.update(id=user_id, item_in=user_in)
