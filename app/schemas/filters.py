import re
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, field_validator, model_validator

from app.core.constants import SLUG_REGEX


class PaginationOut(BaseModel):
    offset: int
    limit: int
    total: int


class PaginationIn(BaseModel):
    offset: int = Query(default=0, ge=0, description="Page number")
    limit: int = Query(default=20, ge=1, le=40, description="Page limit")


class ProductFiltersSchema(BaseModel):
    category_slug: Optional[str] = Query(default=None)
    text: Optional[str] = Query(default=None)
    min_price: Optional[float] = Query(default=None, ge=0)
    max_price: Optional[float] = Query(default=None, ge=0)
    diameter: Optional[str] = Query(max_length=20, default=None)
    length: Optional[str] = Query(max_length=20, default=None)
    thickness: Optional[str] = Query(max_length=20, default=None)
    angle: Optional[str] = Query(max_length=20, default=None)
    metal_type: Optional[str] = Query(max_length=50, default=None)

    @field_validator("category_slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and not re.match(SLUG_REGEX, v):
            raise ValueError("Slug має містити тільки a-z, 0-9, '-' та '_'")
        return v.lower() if v else v

    @model_validator(mode="after")
    def validate_price(self):
        if self.min_price and self.max_price and self.min_price > self.max_price:
            raise ValueError("Мінімальна ціна не може бути більшою за максимальну")
        return self


class SortOrderSchema(BaseModel):
    field: str = Query(
        default="created_at",
        pattern="^(final_price|created_at)$",
    )
    ordering: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    )


class MessageSortOrderSchema(BaseModel):
    field: str = Query(
        default="created_at",
        pattern="^(user_name|phone_number|created_at|message|status)$",
    )
    ordering: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    )


class MessageFiltersSchema(BaseModel):
    status: Optional[str] = Query(default=None, pattern="^(new|progress|read)$")
    text: Optional[str] = Query(default=None)


class OrderSortOrderSchema(BaseModel):
    field: str = Query(
        default="created_at",
        pattern="^(id|created_at|last_name|first_name|patronymic|phone_number|email"
        "|status|shipping_method|payment_method|price_discount|is_paid)$",
    )
    ordering: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
    )


class OrderFiltersSchema(BaseModel):
    text: Optional[str] = Query(default=None)
    status: Optional[str] = Query(default=None, pattern="^(pending|processing|shipped|delivered|cancelled)$")
    shipping_method: Optional[str] = Query(default=None, pattern="^(nova_poshta|ukrposhta|courier)$")
    payment_method: Optional[str] = Query(default=None, pattern="^(cash|card|online)$")


class UniqueProductSortOrderSchema(MessageSortOrderSchema):
    pass


class UniqueProductFiltersSchema(BaseModel):
    category_id: Optional[int] = Query(default=None)
    text: Optional[str] = Query(default=None)


class FiltersSchema(BaseModel):
    diameter: list[str | None] = Query(max_length=20, default_factory=list)
    length: list[str | None] = Query(max_length=20, default_factory=list)
    thickness: list[str | None] = Query(max_length=20, default_factory=list)
    angle: list[str | None] = Query(max_length=20, default_factory=list)
    metal_type: list[str | None] = Query(max_length=50, default_factory=list)


class PriceRangeSchema(BaseModel):
    min_price: Optional[float] = Query(default=None, ge=0)
    max_price: Optional[float] = Query(default=None, ge=0)


class CatalogFiltersSchema(FiltersSchema, PriceRangeSchema):
    pass
