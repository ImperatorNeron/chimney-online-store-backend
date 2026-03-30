import os

from app.mappers.base import BaseReadMapper, BaseUpsertMapper
from app.models.faq import FAQ
from app.models.product_images import ProductImage
from app.schemas.faq import CreateFAQSchema, ReadFAQSchema, UpdadeFAQSchema
from app.schemas.product_images import CreateProductImageSchema, ReadProductImageSchema


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

class ProductImageCreateMapper(BaseUpsertMapper[ProductImage, CreateProductImageSchema]):
    pass


# class FaqUpdateMapper(BaseUpsertMapper[FAQ, UpdadeFAQSchema]):
#     pass
