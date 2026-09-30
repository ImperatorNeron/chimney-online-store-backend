from abc import abstractmethod
from typing import Type

from app.mappers.users import UserReadMapper, UserUpdateMapper
from app.schemas.users import ReadUserWithPasswordSchema, UpdateUserSchema
from app.services.base import AbstractRead, AbstractUpdate, Read, Update
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractUserService(
    AbstractRead[ReadUserWithPasswordSchema],
    AbstractUpdate[ReadUserWithPasswordSchema, UpdateUserSchema],
):

    @abstractmethod
    async def get_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> ReadUserWithPasswordSchema | None: ...

    @abstractmethod
    async def get_user_by_email(
        self,
        uow: AbstractUnitOfWork,
        email: str,
    ) -> ReadUserWithPasswordSchema | None: ...

    @abstractmethod
    async def get_user_by_phone_number(
        self,
        uow: AbstractUnitOfWork,
        phone_number: str,
    ) -> ReadUserWithPasswordSchema | None: ...


class UserService(
    AbstractUserService,
    Read[ReadUserWithPasswordSchema],
    Update[ReadUserWithPasswordSchema, UpdateUserSchema],
):
    repository_name: str = "users"
    _read_mapper: Type[UserReadMapper] = UserReadMapper
    read_mapper = read_update_mapper = _read_mapper
    update_mapper: Type[UserUpdateMapper] = UserUpdateMapper

    async def get_user_by_username(
        self,
        uow: AbstractUnitOfWork,
        username: str,
    ) -> ReadUserWithPasswordSchema | None:
        if (user := await uow.users.get_or_none(username=username)) is not None:
            return self.read_mapper.to_dto(user)

    async def get_user_by_email(
        self,
        uow: AbstractUnitOfWork,
        email: str,
    ) -> ReadUserWithPasswordSchema | None:
        if (user := await uow.users.get_or_none(email=email)) is not None:
            return self.read_mapper.to_dto(user)

    async def get_user_by_phone_number(
        self,
        uow: AbstractUnitOfWork,
        phone_number: str,
    ) -> ReadUserWithPasswordSchema | None:
        if (user := await uow.users.get_or_none(phone_number=phone_number)) is not None:
            return self.read_mapper.to_dto(user)
