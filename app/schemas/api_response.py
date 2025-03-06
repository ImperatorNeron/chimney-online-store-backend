from typing import (
    Any,
    Generic,
    TypeVar,
)

from pydantic import (
    BaseModel,
    Field,
)

from app.schemas.filters import PaginationOut


TData = TypeVar("TData")
TListItem = TypeVar("TListItem")


class ListPaginatedResponse(BaseModel, Generic[TListItem]):
    items: list[TListItem]
    pagination: PaginationOut


class ApiResponseSchema(BaseModel, Generic[TData]):
    data: TData | dict = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    errors: list[Any] = Field(default_factory=list)
