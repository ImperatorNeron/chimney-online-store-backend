from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

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
    metal_type: Optional[str] = Field(max_length=50)


class ReadPreviewProductSchema(ReadProductSchema):
    preview: Optional[ReadProductImageSchema]


class ReadFullProductSchema(ReadProductSchema):
    images: list[ReadProductImageSchema]


class ReadFullProductWithCategoryHierarchySchema(ReadFullProductSchema):
    categories: list[list[str]]


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
        None,
        min_length=2,
        max_length=200,
        example="Sample Product",
    )
    slug: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        example="sample-product",
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
    metal_type: Optional[str] = Field(max_length=50)
    min_price: Optional[str] = Field(max_length=20)
    max_price: Optional[str] = Field(max_length=20)


# -----------------------------------------------


class ReadProductVariationSchema(BaseModel):
    id: int = Field(ge=0)  # noqa
    created_at: datetime
    updated_at: datetime
    price: float = Field(ge=0, example=19.99)
    discount_price: float = Field(ge=0, example=19.99)
    discount_percentage: int = Field(ge=0, le=100, example=20)
    diameter: Optional[str] = Field(max_length=20)
    length: Optional[str] = Field(max_length=20)
    thickness: Optional[str] = Field(max_length=20)
    angle: Optional[str] = Field(max_length=20)
    metal_type: Optional[str] = Field(max_length=50)


class BaseCreateProductVariationSchema(BaseModel):
    price: float = Field(ge=0)
    discount_percentage: Optional[int] = Field(ge=0, le=100, default=0)
    diameter: Optional[str] = None
    length: Optional[str] = None
    thickness: Optional[str] = None
    angle: Optional[str] = None
    metal_type: Optional[str] = None


class CreateProductVariationSchema(BaseCreateProductVariationSchema):
    product_id: int = Field(gt=0)


# Full Schema ----------------------------------------------


class ReadAbsoluteProductSchema(ReadFullUniqueProductSchema):
    variations: list[ReadProductVariationSchema]
    categories: Optional[list[tuple[str, str]]] = None


class VariationAction(str, Enum):
    create = "create"
    update = "update"
    delete = "delete"


class IDSchema(BaseModel):
    id: Optional[int] = None  # noqa


class BaseUpdateVariationSchema(BaseModel):
    price: Optional[float] = Field(ge=0, default=None)
    discount_percentage: Optional[int] = Field(ge=0, le=100, default=None)
    diameter: Optional[str] = None
    length: Optional[str] = None
    thickness: Optional[str] = None
    angle: Optional[str] = None
    metal_type: Optional[str] = None


class UpdateVariationSchema(BaseUpdateVariationSchema, IDSchema):
    action: VariationAction

    @model_validator(mode="after")
    def validate_id_for_update_delete(self):
        if self.action in (VariationAction.update, VariationAction.delete) and self.id is None:
            raise ValueError("id is required for update/delete")
        return self


class FullUpdateVariationSchema(BaseUpdateVariationSchema, IDSchema):
    product_id: int = Field(gt=0)
