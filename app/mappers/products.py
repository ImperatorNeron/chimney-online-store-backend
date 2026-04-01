import os

from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.product_images import ProductImage
from app.models.products import ProductVariation, UniqueProduct
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.schemas.products import (
    CreateUniqueProductSchema,
    ReadFullProductSchema,
    ReadFullUniqueProductSchema,
    ReadPreviewProductSchema,
    ReadProductSchema,
    ReadProductVariationSchema,
    ReadUniqueProductSchema,
    UpdateUniqueProductSchema,
)


class ProductImageReadMapper(BaseReadMapper[ProductImage, ReadProductImageSchema]):

    @staticmethod
    def to_dto(orm_obj: ProductImage) -> ReadProductImageSchema:
        return ReadProductImageSchema(
            id=orm_obj.id,
            alt=orm_obj.alt,
            file_path=orm_obj.file_path,
            filename=os.path.basename(orm_obj.file_path),
            product_id=orm_obj.product_id,
        )


class ProductImageCreateMapper(
    BaseUpsertMapper[ProductImage, CreateProductImageSchema],
):
    pass


# class FaqUpdateMapper(BaseUpsertMapper[FAQ, UpdadeFAQSchema]):
#     pass


class UniqueProductReadMapper(BaseReadMapper[UniqueProduct, ReadUniqueProductSchema]):

    @staticmethod
    def to_dto(orm_obj: UniqueProduct) -> ReadUniqueProductSchema:
        return ReadUniqueProductSchema(
            id=orm_obj.id,
            name=orm_obj.name,
            slug=orm_obj.slug,
            description=orm_obj.description,
            category_id=orm_obj.category_id,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
        )


class FullUniqueProductReadMapper(
    BaseReadMapper[UniqueProduct, ReadFullUniqueProductSchema],
):

    @staticmethod
    def to_dto(orm_obj: UniqueProduct) -> ReadFullUniqueProductSchema:
        return ReadFullUniqueProductSchema(
            **UniqueProductReadMapper.to_dto(orm_obj).model_dump(),
            images=ProductImageReadMapper.to_dto_list(orm_objs=orm_obj.images),
        )


class UniqueProductCreateMapper(
    BaseUpsertMapper[UniqueProduct, CreateUniqueProductSchema],
):
    pass


class UniqueProductUpdateMapper(
    BaseUpsertMapper[UniqueProduct, UpdateUniqueProductSchema],
):
    pass


class ProductVariationReadMapper(BaseReadMapper[ProductVariation, ReadProductSchema]):
    @staticmethod
    def to_dto(orm_obj: ProductVariation) -> ReadProductSchema:
        return ReadProductSchema(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            name=orm_obj.product.name,
            slug=orm_obj.product.slug,
            description=orm_obj.product.description,
            price=orm_obj.price,
            discount_price=round(
                orm_obj.price - orm_obj.price * orm_obj.discount_percentage / 100,
                2,
            ),
            discount_percentage=orm_obj.discount_percentage,
            category_id=orm_obj.product.category_id,
            extra_attrs=orm_obj.extra_attrs,
            diameter=orm_obj.diameter,
            length=orm_obj.length,
            thickness=orm_obj.thickness,
            angle=orm_obj.angle,
            metal_type=orm_obj.metal_type,
        )


class BaseProductVariationReadMapper(
    BaseReadMapper[ProductVariation, ReadProductVariationSchema],
):
    @staticmethod
    def to_dto(orm_obj: ProductVariation) -> ReadProductVariationSchema:
        return ReadProductVariationSchema(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            price=orm_obj.price,
            discount_price=orm_obj.price
            - (orm_obj.price * orm_obj.discount_percentage) / 100,
            discount_percentage=orm_obj.discount_percentage,
            diameter=orm_obj.diameter,
            length=orm_obj.length,
            thickness=orm_obj.thickness,
            angle=orm_obj.angle,
            metal_type=orm_obj.metal_type,
        )


class PreviewProductVariationReadMapper(
    BaseReadMapper[ProductVariation, ReadPreviewProductSchema],
):
    @staticmethod
    def to_dto(orm_obj: ProductVariation) -> ReadPreviewProductSchema:
        preview = (
            ProductImageReadMapper.to_dto(orm_obj=orm_obj.product.images[0])
            if orm_obj.product.images
            else None
        )
        return ReadPreviewProductSchema(
            ProductVariationReadMapper.to_dto(orm_obj=orm_obj),
            preview=preview,
        )


class FullProductVariationReadMapper(
    BaseReadMapper[ProductVariation, ReadFullProductSchema],
):
    @staticmethod
    def to_dto(orm_obj: ProductVariation) -> ReadFullProductSchema:
        return ReadFullProductSchema(
            ProductVariationReadMapper.to_dto(orm_obj=orm_obj),
            images=ProductImageReadMapper.to_dto_list(orm_objs=orm_obj.product.images),
        )
