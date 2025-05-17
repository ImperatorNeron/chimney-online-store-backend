from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.product_images import ReadProductImageSchema
from app.schemas.validators import SlugValidatorMixin


class BaseProductSchema(BaseModel, SlugValidatorMixin):
    name: str = Field(..., min_length=2, max_length=200, example="Sample Product")
    slug: str = Field(..., min_length=2, max_length=255, example="sample-product")
    description: Optional[str] = Field(
        None,
        example="This is a sample product description.",
    )
    price: float = Field(gt=0, example=19.99)
    extra_attrs: Optional[dict]
    category_id: int = Field(..., ge=0, example=1)


class ReadProductSchema(BaseProductSchema):
    id: int = Field(ge=0)  # noqa
    created_at: datetime
    updated_at: datetime
    discount_price: float = Field(ge=0, example=19.99)
    discount_percentage: int = Field(ge=0, le=100, example=20)
    diameter: Optional[str] = Field(max_length=20)
    length: Optional[str] = Field(max_length=20)
    thickness: Optional[str] = Field(max_length=20)
    angle: Optional[str] = Field(max_length=20)
    metal_type: Optional[str] = Field(max_length=20)


class ReadPreviewProductSchema(ReadProductSchema):
    preview: Optional[ReadProductImageSchema]


class ReadFullProductSchema(ReadProductSchema):
    images: list[ReadProductImageSchema]


# -----------------------------------------------


class ReadUniqueProductSchema(BaseModel, SlugValidatorMixin):
    id: int  # noqa
    name: str = Field(..., min_length=2, max_length=200, example="Sample Product")
    slug: str = Field(..., min_length=2, max_length=255, example="sample-product")
    description: Optional[str] = Field(
        None,
        example="This is a sample product description.",
    )
    category_id: int = Field(..., ge=0, example=1)
    created_at: datetime
    updated_at: datetime


class ReadFullUniqueProductSchema(ReadUniqueProductSchema):
    images: list[ReadProductImageSchema]


class CreateUniqueProductSchema(BaseModel, SlugValidatorMixin):
    name: str = Field(..., min_length=2, max_length=200, example="Sample Product")
    slug: str = Field(..., min_length=2, max_length=255, example="sample-product")
    description: Optional[str] = Field(
        None,
        example="This is a sample product description.",
    )
    category_id: int = Field(..., ge=0, example=1)


class UpdateUniqueProductSchema(BaseModel):
    name: Optional[str] = Field(
        None, min_length=2, max_length=200, example="Sample Product",
    )
    slug: Optional[str] = Field(
        None, min_length=2, max_length=255, example="sample-product",
    )
    description: Optional[str] = Field(
        None,
        example="This is a sample product description.",
    )
    category_id: Optional[int] = Field(None, ge=0, example=1)


class ReadFiltersSchema(BaseModel):
    diameter: Optional[str] = Field(max_length=20)
    length: Optional[str] = Field(max_length=20)
    thickness: Optional[str] = Field(max_length=20)
    angle: Optional[str] = Field(max_length=20)
    metal_type: Optional[str] = Field(max_length=20)
    min_price: Optional[str] = Field(max_length=20)
    max_price: Optional[str] = Field(max_length=20)


# -----------------------------------------------


class ReadProductVariationSchema(BaseModel):
    id: int = Field(ge=0)  # noqa
    created_at: datetime
    updated_at: datetime
    discount_price: float = Field(ge=0, example=19.99)
    discount_percentage: int = Field(ge=0, le=100, example=20)
    diameter: Optional[str] = Field(max_length=20)
    length: Optional[str] = Field(max_length=20)
    thickness: Optional[str] = Field(max_length=20)
    angle: Optional[str] = Field(max_length=20)
    metal_type: Optional[str] = Field(max_length=20)


class BaseCreateProductVariationSchema(BaseModel):
    price: Optional[float] = Field(ge=0, default=None)
    discount_percentage: Optional[int] = Field(default="0")
    diameter: Optional[str] = None
    length: Optional[str] = None
    thickness: Optional[str] = None
    angle: Optional[str] = None
    metal_type: Optional[str] = None


class CreateProductVariationSchema(BaseCreateProductVariationSchema):
    product_id: int = Field(gt=0)
