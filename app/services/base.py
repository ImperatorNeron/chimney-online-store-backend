from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel

from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.utils.sql_repository import AbstractRepository
from app.utils.unit_of_work import AbstractUnitOfWork


DTOReadType = TypeVar("DTOReadType", bound=BaseModel)
DTOCreateType = TypeVar("DTOCreateType", bound=BaseModel)
DTOUpdateType = TypeVar("DTOUpdateType", bound=BaseModel)


class AbstractRead(ABC, Generic[DTOReadType]):
    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
        filters: BaseModel | dict | None = None,
        pagination_in: BaseModel | None = None,
        order_by: BaseModel | None = None,
    ) -> list[DTOReadType]: ...

    @abstractmethod
    async def get_one(
        self,
        uow: AbstractUnitOfWork,
        conditions: BaseModel | dict,
    ) -> DTOReadType: ...


class AbstractCreate(ABC, Generic[DTOReadType, DTOCreateType]):
    @abstractmethod
    async def create(
        self,
        item_in: DTOCreateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType: ...

    @abstractmethod
    async def bulk_create(
        self,
        items_in: list[DTOCreateType],
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
        uow: AbstractUnitOfWork,
        **conditions: Any,
    ) -> None: ...

    @abstractmethod
    async def bulk_delete(
        self,
        uow: AbstractUnitOfWork,
        **conditions,
    ) -> None: ...


class AbstractCount(ABC):
    @abstractmethod
    async def count(
        self,
        uow: AbstractUnitOfWork,
        filters: BaseModel | dict | None = None,
    ) -> int: ...


class AbstractCRUDService(
    AbstractRead[DTOReadType],
    AbstractCreate[DTOReadType, DTOCreateType],
    AbstractUpdate[DTOReadType, DTOUpdateType],
    AbstractDelete,
    AbstractCount,
    Generic[DTOReadType, DTOCreateType, DTOUpdateType],
):
    pass


class RepositoryMixin:
    repository_name: str | None = None

    def _repository(self, uow: AbstractUnitOfWork) -> AbstractRepository:
        return getattr(uow, self.repository_name)


class Read(AbstractRead[DTOReadType], RepositoryMixin):
    read_mapper: Type[BaseReadMapper] = None

    @staticmethod
    def _prepare_list_params(
        filters: BaseModel | dict | None = None,
        pagination_in: BaseModel | None = None,
        order_by: BaseModel | None = None,
    ) -> dict:
        order_by_fields = []
        if order_by is not None:
            directioned_field = order_by.field
            if order_by.ordering == "desc":
                directioned_field = f"-{directioned_field}"
            order_by_fields.append(directioned_field)

        limit = None
        offset = None
        if pagination_in is not None:
            limit = pagination_in.limit
            offset = pagination_in.offset

        filters_dict = None
        if filters is not None:
            if isinstance(filters, BaseModel):
                filters_dict = filters.model_dump()
            elif isinstance(filters, dict):
                filters_dict = filters

        return {
            "filters": filters_dict,
            "order_by": order_by_fields,
            "limit": limit,
            "offset": offset,
        }

    async def list_all(
        self,
        uow: AbstractUnitOfWork,
        filters: BaseModel | dict | None = None,
        pagination_in: BaseModel | None = None,
        order_by: BaseModel | None = None,
    ) -> list[DTOReadType]:
        await self._validate_list_all(
            uow=uow,
            filters=filters,
            pagination_in=pagination_in,
            order_by=order_by,
        )
        return self.read_mapper.to_dto_list(
            await self._repository(uow).all(
                **self._prepare_list_params(filters, pagination_in, order_by),
            ),
        )

    async def get_one(
        self,
        uow: AbstractUnitOfWork,
        conditions: BaseModel | dict,
    ) -> DTOReadType:
        if isinstance(conditions, BaseModel):
            conditions = conditions.model_dump()
        return self.read_mapper.to_dto(await self._repository(uow).get(**conditions))

    async def _validate_list_all(self, *args, **kwargs):
        pass


class Create(
    AbstractCreate[DTOReadType, DTOCreateType],
    RepositoryMixin,
):
    read_create_mapper: Type[BaseReadMapper] = None
    create_mapper: Type[BaseUpsertMapper] = None

    async def _create_validation(self, *args, **kwargs):
        pass

    async def _bulk_create_validation(self, *args, **kwargs):
        pass

    async def create(
        self,
        item_in: DTOCreateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType:
        await self._create_validation(item_in=item_in, uow=uow)
        return self.read_create_mapper.to_dto(
            await self._repository(uow).create(
                item_in=self.create_mapper.to_model(item_in),
            ),
        )

    async def bulk_create(
        self,
        items_in: list[DTOCreateType],
        uow: AbstractUnitOfWork,
    ) -> DTOReadType:
        await self._bulk_create_validation(items_in=items_in, uow=uow)
        return self.read_create_mapper.to_dto_list(
            await self._repository(uow).bulk_create(
                data_list=self.create_mapper.to_model_list(items_in),
            ),
        )


class Update(AbstractUpdate[DTOReadType, DTOUpdateType], RepositoryMixin):
    read_update_mapper: Type[BaseReadMapper] = None
    update_mapper: Type[BaseUpsertMapper] = None

    async def _update_validation(self, *args, **kwargs):
        pass

    async def update(
        self,
        item_id: int,
        item_in: DTOUpdateType,
        uow: AbstractUnitOfWork,
    ) -> DTOReadType:
        await self._update_validation(item_id=item_id, item_in=item_in, uow=uow)
        res = await self._repository(uow).update(
            id=item_id,
            item_in=self.update_mapper.to_model(item_in),
        )
        return self.read_update_mapper.to_dto(
            res,
        )


class Delete(AbstractDelete, RepositoryMixin):

    async def delete(
        self,
        uow: AbstractUnitOfWork,
        **conditions,
    ) -> None:
        await self._delete_validation(**conditions)
        await self._repository(uow).delete(**conditions)

    async def bulk_delete(
        self,
        uow: AbstractUnitOfWork,
        **conditions,
    ) -> None:
        await self._bulk_delete_validation(**conditions)
        await self._repository(uow).bulk_delete(**conditions)

    async def _delete_validation(self, *args, **kwargs):
        pass

    async def _bulk_delete_validation(self, *args, **kwargs):
        pass


class Count(AbstractCount, RepositoryMixin):

    async def count(
        self,
        uow: AbstractUnitOfWork,
        filters: BaseModel | dict | None = None,
    ) -> int:
        filters_dict = None
        if filters is not None:
            if isinstance(filters, BaseModel):
                filters_dict = filters.model_dump()
            elif isinstance(filters, dict):
                filters_dict = filters
        return await self._repository(uow).count(
            **filters_dict if filters_dict is not None else {},
        )


class CRUDService(
    AbstractCRUDService[DTOReadType, DTOCreateType, DTOUpdateType],
    Read[DTOReadType],
    Create[DTOReadType, DTOCreateType],
    Update[DTOReadType, DTOUpdateType],
    Delete,
    Count,
    Generic[DTOReadType, DTOCreateType, DTOUpdateType],
):
    pass
