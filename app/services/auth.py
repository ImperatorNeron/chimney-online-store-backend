from typing import Type

from app.mappers.users import UserCreateMapper, UserReadMapper
from app.schemas.users import CreateUserSchema, ReadUserWithPasswordSchema
from app.services.base import AbstractCreate, Create


class AbstractAuthService(AbstractCreate[ReadUserWithPasswordSchema, CreateUserSchema]):
    pass


class AuthService(AbstractAuthService, Create[ReadUserWithPasswordSchema, CreateUserSchema]):
    repository_name: str = "users"
    read_create_mapper: Type[UserReadMapper] = UserReadMapper
    create_mapper: Type[UserCreateMapper] = UserCreateMapper
