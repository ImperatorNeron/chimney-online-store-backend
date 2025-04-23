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
    characteristics: Optional[dict]
    category_id: int = Field(..., ge=0, example=1)


class ReadProductSchema(BaseProductSchema):
    id: int = Field(ge=0)  # noqa
    created_at: datetime
    updated_at: datetime
    discount_price: float = Field(ge=0, example=19.99)
    discount_percentage: int = Field(ge=0, le=100, example=20)


class CreateProductSchema(BaseProductSchema):
    pass


class ReadPreviewProductSchema(ReadProductSchema):
    preview: Optional[ReadProductImageSchema]


class ReadFullProductSchema(ReadProductSchema):
    images: list[ReadProductImageSchema]
