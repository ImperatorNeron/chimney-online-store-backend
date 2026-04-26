import os

from app.core import constants
from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.base import BaseModel as Model
from app.models.product_images import ProductImage
from app.models.products import ProductVariation, UniqueProduct
from app.schemas.filters import FiltersSchema, PriceRangeSchema
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema
from app.schemas.products import (
    BaseCreateProductVariationSchema,
    BaseUpdateVariationSchema,
    CreateProductVariationSchema,
    CreateUniqueProductSchema,
    FullUpdateVariationSchema,
    ReadFullProductSchema,
    ReadFullUniqueProductSchema,
    ReadPreviewProductSchema,
    ReadProductSchema,
    ReadProductVariationSchema,
    ReadUniqueProductSchema,
    UpdateUniqueProductSchema,
    UpdateVariationSchema,
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
    def to_dto(orm_obj: ProductVariation, **kwargs) -> ReadProductSchema:
        ws = kwargs.get("website_settings")
        price = float(orm_obj.price)
        if ws:
            price = price * (1 - ws.manufacturer_discount / 100) * (1 + ws.seller_markup / 100)
        discount_price = round(price - price * orm_obj.discount_percentage / 100)
        return ReadProductSchema(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            name=orm_obj.product.name,
            slug=orm_obj.product.slug,
            description=orm_obj.product.description,
            price=round(price),
            discount_price=discount_price,
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
    def to_dto(orm_obj: ProductVariation, **kwargs) -> ReadProductVariationSchema:
        ws = kwargs.get("website_settings")
        price = float(orm_obj.price)
        if ws:
            price = price * (1 - ws.manufacturer_discount / 100) * (1 + ws.seller_markup / 100)
        discount_price = round(price - (price * orm_obj.discount_percentage) / 100)
        return ReadProductVariationSchema(
            id=orm_obj.id,
            created_at=orm_obj.created_at,
            updated_at=orm_obj.updated_at,
            price=round(price),
            discount_price=discount_price,
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
    def to_dto(orm_obj: ProductVariation, **kwargs) -> ReadPreviewProductSchema:
        preview = (
            ProductImageReadMapper.to_dto(orm_obj=orm_obj.product.images[0])
            if orm_obj.product.images
            else None
        )
        return ReadPreviewProductSchema(
            **ProductVariationReadMapper.to_dto(orm_obj=orm_obj, **kwargs).model_dump(),
            preview=preview,
        )


class FullProductVariationReadMapper(
    BaseReadMapper[ProductVariation, ReadFullProductSchema],
):
    @staticmethod
    def to_dto(orm_obj: ProductVariation, **kwargs) -> ReadFullProductSchema:
        return ReadFullProductSchema(
            ProductVariationReadMapper.to_dto(orm_obj=orm_obj, **kwargs),
            images=ProductImageReadMapper.to_dto_list(orm_objs=orm_obj.product.images),
        )


class ProductVariationCreateMapper(
    BaseUpsertMapper[ProductVariation, FullUpdateVariationSchema],
):
    pass


class ProductVariationUpdateMapper(
    BaseUpsertMapper[ProductVariation, BaseUpdateVariationSchema],
):
    pass


class ProductVariationToBaseProductVariationUpdateMapper(
    BaseReadMapper[UpdateVariationSchema, BaseUpdateVariationSchema],
):
    @staticmethod
    def to_dto(orm_obj: UpdateVariationSchema) -> BaseUpdateVariationSchema:
        return BaseUpdateVariationSchema(**orm_obj.model_dump(exclude={"action", "id"}))


class BaseProductVariationToProductVariationCreateMapper(
    BaseReadMapper[BaseCreateProductVariationSchema, CreateProductVariationSchema],
):
    @staticmethod
    def to_dto(
        orm_obj: BaseCreateProductVariationSchema, **kwargs,
    ) -> CreateProductVariationSchema:
        return CreateProductVariationSchema(
            **orm_obj.model_dump(), product_id=kwargs.get("product_id"),
        )


class ProductVariationToFullProductVariationUpdateMapper(
    BaseReadMapper[UpdateVariationSchema, FullUpdateVariationSchema],
):
    @staticmethod
    def to_dto(orm_obj: UpdateVariationSchema, **kwargs) -> FullUpdateVariationSchema:
        return FullUpdateVariationSchema(
            **orm_obj.model_dump(), product_id=kwargs.get("product_id"),
        )


class ProductFiltersReadMapper(BaseReadMapper[Model, FiltersSchema]):
    @staticmethod
    def to_dto(orm_obj: Model, **kwargs) -> FiltersSchema:
        return FiltersSchema(
            **{
                attr: [
                    str(v)
                    for v in (getattr(orm_obj, attr) or [])
                    if v is not None and v != ""
                ]
                for attr in constants.FILTERS
            },
        )


class PriceRangeReadMapper(BaseReadMapper[Model, PriceRangeSchema]):

    @staticmethod
    def to_dto(orm_obj: Model, **kwargs) -> PriceRangeSchema:
        return PriceRangeSchema(
            min_price=round(orm_obj[0]) if orm_obj[0] is not None else 0,
            max_price=round(orm_obj[1]) if orm_obj[1] is not None else 0,
        )
