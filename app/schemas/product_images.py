from typing import Optional

from pydantic import BaseModel, Field


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
