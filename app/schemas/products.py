from datetime import datetime
from typing import Optional

from fastapi import Form
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
    category_id: int = Field(..., ge=0, example=1)


class ReadProductSchema(BaseProductSchema):
    id: int = Field(ge=0)  # noqa
    created_at: datetime
    updated_at: datetime


class CreateProductSchema(BaseProductSchema):
    pass


class ProductForm(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    category_id: int

    @classmethod
    def from_form(
        cls,
        name: str = Form(...),
        slug: str = Form(...),
        description: Optional[str] = Form(None),
        price: float = Form(...),
        category_id: int = Form(...),
    ):
        return cls(
            name=name,
            slug=slug,
            description=description,
            price=price,
            category_id=category_id,
        )


class ReadPreviewProductSchema(ReadProductSchema):
    preview: Optional[ReadProductImageSchema]


class ReadFullProductSchema(ReadProductSchema):
    images: list[ReadProductImageSchema]
