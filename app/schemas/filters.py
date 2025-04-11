import re
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, field_validator

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

    @field_validator("category_slug")
    @classmethod
    def validate_slug(cls, v):
        if v is not None and not re.match(SLUG_REGEX, v):
            raise ValueError("Slug має містити тільки a-z, 0-9, '-' та '_'")
        return v.lower() if v else v


class SortOrderSchema(BaseModel):
    field: str = Query(
        default="created_at",
        pattern="^(final_price|created_at)$",
    )
    ordering: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    )
