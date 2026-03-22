from abc import ABC, abstractmethod

from app.core.exceptions.common import (
    ForeignKeyConstraintViolationException,
    UniqueConstraintViolationsException,
)
from app.schemas.categories import (
    CreateCategorySchema,
    ReadCategorySchema,
    UpdateCategorySchema,
)
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

    @abstractmethod
    async def get_category_hierarchy(
        self,
        category_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[list[str]]: ...

    @abstractmethod
    async def get_category_names_from_slugs(
        self,
        slugs: list[list[str]],
        uow: AbstractUnitOfWork,
    ) -> list[str]: ...

    @abstractmethod
    async def get_children_by_parent_ids(
        self,
        parent_ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]: ...


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
        if category_in.parent_id and not await uow.categories.exists(
            id=category_in.parent_id,
        ):
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

    async def get_category_hierarchy(
        self,
        category_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[list[str]]:
        return await uow.categories.get_category_hierarchy(category_id=category_id)

    async def get_category_names_from_slugs(
        self,
        slugs: list[str],
        uow: AbstractUnitOfWork,
    ) -> list[list[str]]:
        return await uow.categories.get_category_names_from_slugs(slugs=slugs)

    async def get_children_by_parent_ids(
        self,
        parent_ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        return await uow.categories.all(filters={"parent_id__in": parent_ids})
