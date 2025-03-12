from abc import ABC, abstractmethod

from app.schemas.categories import CreateCategorySchema, ReadCategorySchema, UpdateCategorySchema
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCategoryService(ABC):

    @abstractmethod
    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]: ...

    @abstractmethod
    async def create(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
    ): ...

    @abstractmethod
    async def update(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
    ): ...


class CategoryService(AbstractCategoryService):

    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        return await uow.categories.fetch_all()

    async def create(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
    ):
        return await uow.categories.create(item_in=category_in)

    async def update(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
    ):
        return await uow.categories.update_by_id(
            item_id=category_id,
            item_in=category_in,
        )
