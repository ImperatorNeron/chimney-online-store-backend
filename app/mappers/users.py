from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.users import User
from app.schemas.users import CreateUserSchema, ReadUserWithPasswordSchema, UpdateUserSchema


class UserReadMapper(BaseReadMapper[User, ReadUserWithPasswordSchema]):

    @staticmethod
    def to_dto(orm_obj: User) -> ReadUserWithPasswordSchema:
        return ReadUserWithPasswordSchema(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            email=orm_obj.email,
            phone_number=orm_obj.phone_number,
            username=orm_obj.username,
            is_verified=orm_obj.is_verified,
            is_active=orm_obj.is_active,
            is_superuser=orm_obj.is_superuser,
            first_name=orm_obj.first_name,
            last_name=orm_obj.last_name,
            patronymic=orm_obj.patronymic,
            hashed_password=orm_obj.hashed_password,
        )


class UserCreateMapper(BaseUpsertMapper[User, CreateUserSchema]):
    pass


class UserUpdateMapper(BaseUpsertMapper[User, UpdateUserSchema]):
    pass
