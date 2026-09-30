from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.categories import Category
from app.schemas.categories import (
    CreateCategorySchema,
    ReadCategoryNameSlugSchema,
    ReadCategorySchema,
    UpdateCategorySchema,
)


class CategoryReadMapper(BaseReadMapper[Category, ReadCategorySchema]):

    @staticmethod
    def to_dto(orm_obj: Category) -> ReadCategorySchema:
        return ReadCategorySchema(
            id=orm_obj.id,
            name=orm_obj.name,
            slug=orm_obj.slug,
            file_path=orm_obj.file_path,
            parent_id=orm_obj.parent_id,
        )


class CategoryCreateMapper(BaseUpsertMapper[Category, CreateCategorySchema]):
    pass


class CategoryUpdateMapper(BaseUpsertMapper[Category, UpdateCategorySchema]):
    pass


class CategoryNameSlugMapper(BaseReadMapper[Category, ReadCategoryNameSlugSchema]):

    @staticmethod
    def to_dto(orm_obj: Category) -> ReadCategoryNameSlugSchema:
        return ReadCategoryNameSlugSchema(name=orm_obj.name, slug=orm_obj.slug)
