from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.validators import SlugValidatorMixin


class ProductImageBase(BaseModel):
    file_path: str = Field(
        ...,
        min_length=2,
        max_length=512,
        example="/images/products/sample.jpg",
    )
    alt: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        example="Sample product image",
    )
    product_id: int = Field(..., ge=0, example=1)


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageRead(ProductImageBase):
    id: int = Field(ge=0)  # noqa


class BaseProductSchema(BaseModel, SlugValidatorMixin):
    name: str = Field(..., min_length=2, max_length=200, example="Sample Product")
    slug: str = Field(..., min_length=2, max_length=255, example="sample-product")
    description: Optional[str] = Field(
        None,
        example="This is a sample product description.",
    )
    price: float = Field(..., gt=0, example=19.99)
    category_id: int = Field(..., ge=0, example=1)


class ReadProductSchema(BaseProductSchema):
    id: int = Field(ge=0)  # noqa
    created_at: datetime
    updated_at: datetime


class ReadPreviewProductSchema(ReadProductSchema):
    preview: Optional[ProductImageRead]


class ReadFullProductSchema(ReadProductSchema):
    images: list[ProductImageRead]
