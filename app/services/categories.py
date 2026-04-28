from abc import abstractmethod
from typing import Type

from app.core.exceptions.common import ForeignKeyConstraintViolationException, UniqueConstraintViolationsException
from app.mappers.categories import (
    CategoryCreateMapper,
    CategoryNameSlugMapper,
    CategoryReadMapper,
    CategoryUpdateMapper,
)
from app.schemas.categories import (
    CreateCategorySchema,
    ReadCategoryNameSlugSchema,
    ReadCategorySchema,
    UpdateCategorySchema,
)
from app.services.base import AbstractCRUDService, CRUDService
from app.utils.unit_of_work import AbstractUnitOfWork


class AbstractCategoryService(
    AbstractCRUDService[
        CategoryReadMapper,
        CreateCategorySchema,
        UpdateCategorySchema,
    ],
):

    @abstractmethod
    async def get_category_hierarchy(
        self,
        category_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategoryNameSlugSchema]: ...

    @abstractmethod
    async def get_category_names_from_slugs(
        self,
        slugs: list[list[str]],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategoryNameSlugSchema]: ...

    @abstractmethod
    async def get_children_by_parent_ids(
        self,
        parent_ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]: ...


class CategoryService(AbstractCategoryService, CRUDService):

    repository_name: str = "categories"
    _read_mapper: Type[CategoryReadMapper] = CategoryReadMapper
    read_mapper = read_create_mapper = read_update_mapper = _read_mapper
    read_name_slug_mapper: Type[CategoryNameSlugMapper] = CategoryNameSlugMapper
    create_mapper: Type[CategoryCreateMapper] = CategoryCreateMapper
    update_mapper: Type[CategoryUpdateMapper] = CategoryUpdateMapper

    async def _create_validation(
        self,
        item_in: CreateCategorySchema,
        uow: AbstractUnitOfWork,
    ):
        if await uow.categories.exists(slug=item_in.slug):
            raise UniqueConstraintViolationsException(
                {"slug": "Категорія з цим url вже існує."},
            )

        if item_in.parent_id and not await uow.categories.exists(id=item_in.parent_id):
            raise ForeignKeyConstraintViolationException(
                {"parent_id": "Категорія не існує."},
            )

    async def _update_validation(
        self,
        *args,
        item_id: int,
        item_in: UpdateCategorySchema,
        uow: AbstractUnitOfWork,
        **kwargs,
    ):
        if item_in.slug is not None:
            existing = await uow.categories.get_or_none(slug=item_in.slug)
            if existing and existing.id != item_id:
                raise UniqueConstraintViolationsException(
                    {"slug": "Категорія з цим url вже існує."},
                )
        if item_in.parent_id is not None and not await uow.categories.exists(
            id=item_in.parent_id,
        ):
            raise ForeignKeyConstraintViolationException(
                {"parent_id": "Категорія не існує."},
            )

    async def get_category_hierarchy(
        self,
        category_id: int,
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategoryNameSlugSchema]:
        return self.read_name_slug_mapper.to_dto_list(
            await uow.categories.get_category_hierarchy(category_id=category_id),
        )

    async def get_category_names_from_slugs(
        self,
        slugs: list[str],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategoryNameSlugSchema]:

        if not slugs:
            return []

        return self.read_name_slug_mapper.to_dto_list(
            await uow.categories.get_category_names_from_slugs(slugs=slugs),
        )

    async def get_children_by_parent_ids(
        self,
        parent_ids: list[int],
        uow: AbstractUnitOfWork,
    ) -> list[ReadCategorySchema]:
        return self.read_mapper.to_dto_list(
            await uow.categories.get_children_by_parent_ids(parent_ids),
        )
