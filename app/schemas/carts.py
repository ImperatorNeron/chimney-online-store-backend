from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.cart_items import ReadCartItemWithProductSchema, ReadCartItemWithTotalPriceSchema


class BaseCartSchema(BaseModel):
    user_id: Optional[int] = Field(None, gt=0)
    session_id: Optional[str] = Field(None, min_length=32, max_length=47)

    @model_validator(mode="before")
    @classmethod
    def check_at_least_one_identifier(cls, values):
        user_id = values.get("user_id")
        session_id = values.get("session_id")
        if user_id is None and session_id is None:
            raise ValueError("Either user_id or session_id must be provided")
        return values


class CreateCartSchema(BaseCartSchema):
    pass


class ReadCartSchema(BaseModel):
    id: int = Field(..., ge=0)  # noqa
    items: Optional[list[ReadCartItemWithProductSchema]] = None


class ReadFullCartSchema(BaseModel):
    id: int = Field(..., ge=0)  # noqa
    items: list[ReadCartItemWithTotalPriceSchema]
    total_price: float
    total_quantity: int
