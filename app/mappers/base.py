from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase


ORMType = TypeVar("ORMType", bound=DeclarativeBase)
DTOType = TypeVar("DTOType", bound=BaseModel)


class AbstractMapper(ABC, Generic[ORMType, DTOType]):
    pass


class BaseReadMapper(AbstractMapper[ORMType, DTOType]):

    @staticmethod
    @abstractmethod
    def to_dto(orm_obj: ORMType, **kwargs) -> DTOType: ...

    @classmethod
    def to_dto_list(cls, orm_objs: list[ORMType], **kwargs) -> list[DTOType]:
        return [cls.to_dto(obj, **kwargs) for obj in orm_objs]


class BaseUpsertMapper(AbstractMapper[ORMType, DTOType]):

    orm_class: Type[ORMType] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for base in cls.__orig_bases__:
            if hasattr(base, "__origin__") and base.__origin__ is BaseUpsertMapper:
                cls.orm_class = base.__args__[0]
                break

    @classmethod
    def to_model(cls, dto_obj: DTOType) -> ORMType:
        return cls.orm_class(**dto_obj.model_dump(exclude_none=True))

    @classmethod
    def to_model_list(cls, dto_objs: list[DTOType]) -> list[ORMType]:
        return [cls.to_model(obj) for obj in dto_objs]
