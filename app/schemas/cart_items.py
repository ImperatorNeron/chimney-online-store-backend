from pydantic import BaseModel, Field

from app.schemas.products import ReadPreviewProductSchema


class ReadCartItemSchema(BaseModel):
    id: int = Field(..., gt=0)  # noqa
    cart_id: int = Field(..., ge=0)
    quantity: int = Field(..., ge=1, le=100)
    product_id: int = Field(..., gt=0)


class ReadCartItemWithProductSchema(BaseModel):
    id: int = Field(..., gt=0)  # noqa
    cart_id: int = Field(..., ge=0)
    quantity: int = Field(..., ge=1, le=100)
    product: ReadPreviewProductSchema


class ReadCartItemWithTotalPriceSchema(ReadCartItemWithProductSchema):
    total_price: float


class CreateCartItemSchema(BaseModel):
    cart_id: int = Field(..., ge=0)
    quantity: int = Field(..., ge=1, le=100)
    product_id: int = Field(..., gt=0)


class CreateCartItemWithoutCartIdSchema(BaseModel):
    quantity: int = Field(..., ge=1, le=100)
    product_id: int = Field(..., gt=0)
