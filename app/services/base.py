from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from pydantic import BaseModel

from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.utils.unit_of_work import AbstractUnitOfWork


DTOReadType = TypeVar("DTOReadType", bound=BaseModel)
DTOCreateType = TypeVar("DTOCreateType", bound=BaseModel)
DTOUpdateType = TypeVar("DTOUpdateType", bound=BaseModel)


class AbstractRead(ABC, Generic[DTOReadType]):
    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[DTOReadType]: ...

    @abstractmethod
    async def get_one(
        self,
        item_id: int,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType: ...


class AbstractCreate(ABC, Generic[DTOReadType, DTOCreateType]):
    @abstractmethod
    async def create(
        self,
        item_in: DTOCreateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType: ...


class AbstractUpdate(ABC, Generic[DTOReadType, DTOUpdateType]):
    @abstractmethod
    async def update(
        self,
        item_id: int,
        item_in: DTOUpdateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType: ...


class AbstractDelete(ABC):
    @abstractmethod
    async def delete(
        self,
        item_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


class AbstractCRUDService(
    AbstractRead[DTOReadType],
    AbstractCreate[DTOReadType, DTOCreateType],
    AbstractUpdate[DTOReadType, DTOUpdateType],
    AbstractDelete,
    Generic[DTOReadType, DTOCreateType, DTOUpdateType],
):
    pass


class RepositoryMixin:
    repository_name: str | None = None

    def _repository(self, uow: AbstractUnitOfWork):
        return getattr(uow, self.repository_name)


class Read(AbstractRead[DTOReadType], RepositoryMixin):
    read_mapper: Type[BaseReadMapper] = None

    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[DTOReadType]:
        return self.read_mapper.to_dto_list(await self._repository(uow).all())

    async def get_one(
        self,
        item_id: int,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType:
        return self.read_mapper.to_dto(await self._repository(uow).get(id=item_id))


class Create(AbstractCreate[DTOReadType, DTOCreateType], RepositoryMixin):
    read_mapper: Type[BaseReadMapper] = None
    create_mapper: Type[BaseUpsertMapper] = None

    async def create(
        self,
        item_in: DTOCreateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType:
        return self.read_mapper.to_dto(
            await self._repository(uow).create(
                item_in=self.create_mapper.to_model(item_in),
            ),
        )


class Update(AbstractUpdate[DTOReadType, DTOUpdateType], RepositoryMixin):
    read_mapper: Type[BaseReadMapper] = None
    update_mapper: Type[BaseUpsertMapper] = None

    async def update(
        self,
        item_id: int,
        item_in: DTOUpdateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType:
        return self.read_mapper.to_dto(
            await self._repository(uow).update(
                id=item_id, item_in=self.update_mapper.to_model(item_in),
            ),
        )


class Delete(AbstractDelete, RepositoryMixin):

    async def delete(
        self,
        item_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        return await self._repository(uow).delete(id=item_id)


class CRUDService(
    AbstractCRUDService[DTOReadType, DTOCreateType, DTOUpdateType],
    Read[DTOReadType],
    Create[DTOReadType, DTOCreateType],
    Update[DTOReadType, DTOUpdateType],
    Delete,
    Generic[DTOReadType, DTOCreateType, DTOUpdateType],
):
    pass
