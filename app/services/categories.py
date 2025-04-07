from abc import ABC, abstractmethod

from app.core.exceptions.common import ForeignKeyConstraintViolationException, UniqueConstraintViolationsException
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
    ) -> list[ReadCategorySchema]: ...

    @abstractmethod
    async def update(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]: ...

    @abstractmethod
    async def delete(
        self,
        category_id: int,
        uow: AbstractUnitOfWork,
    ) -> None: ...


class CategoryService(AbstractCategoryService):

    async def list_all(
        self,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        return await uow.categories.all()

    async def create(
        self,
        category_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        if await uow.categories.exists(slug=category_in.slug):
            raise UniqueConstraintViolationsException(
                {"slug": "Категорія з цим url вже існує."},
            )
        if category_in.parent_id and not await uow.categories.exists(id=category_in.parent_id):
            raise ForeignKeyConstraintViolationException(
                {"parent_id": "Категорія не існує."},
            )
        return await uow.categories.create(item_in=category_in)

    async def update(
        self,
        category_id: int,
        category_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        if category_in.slug is not None and await uow.categories.exists(
            slug=category_in.slug,
        ):
            raise UniqueConstraintViolationsException(
                {"slug": "Категорія з цим url вже існує."},
            )
        if category_in.parent_id is not None and not await uow.categories.exists(
            id=category_in.parent_id,
        ):
            raise ForeignKeyConstraintViolationException(
                {"parent_id": "Категорія не існує."},
            )
        return await uow.categories.update(
            id=category_id,
            item_in=category_in,
        )

    async def delete(
        self,
        category_id: int,
        uow: AbstractUnitOfWork,
    ) -> None:
        return await uow.categories.delete(id=category_id)
