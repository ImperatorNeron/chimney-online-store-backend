from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.products import ReadProductSchema


class OrderItemFields(BaseModel):
    order_id: int = Field(..., gt=0, description="Must be positive integer")
    quantity: int = Field(..., ge=1, description="At least 1 item")
    price_at_order: float = Field(..., gt=0, description="Must be positive value")


class ReadOrderItemSchema(OrderItemFields):
    id: int = Field(..., description="Order item ID")  # noqa
    product: ReadProductSchema


class ReadOrderItemBaseSchema(OrderItemFields):
    id: int = Field(..., description="Order item ID")  # noqa
    product_id: int = Field(..., gt=0, description="Must be positive integer")


class CreateOrderItemSchema(OrderItemFields):
    product_id: int = Field(..., gt=0, description="Must be positive integer")


class UserIdField(BaseModel):
    user_id: Optional[int] = Field(None, gt=0, description="Must be positive integer")


class OrderFields(BaseModel):
    first_name: str = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="First Name",
        pattern=r"^[\p{L}' -]+$",
        examples=["Your First Name"],
    )
    last_name: str = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Last Name",
        pattern=r"^[\p{L}' -]+$",
        examples=["Your Last Name"],
    )
    patronymic: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Patronymic",
        pattern=r"^[\p{L}' -]+$",
        examples=["Your Patronymic"],
    )
    phone_number: str = Field(
        default=None,
        min_length=9,
        max_length=19,
        title="Phone Number",
        pattern=r"^\d{9,19}$",
        examples=["0961234567"],
    )
    email: Optional[EmailStr] = Field(
        default=None,
        min_length=5,
        max_length=255,
        title="Email address of the user",
    )
    address: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="5-200 characters",
    )
    shipping_method: str = Field(
        ...,
        pattern="^(nova_poshta|ukrposhta|courier)$",
        description="Invalid shipping method",
    )
    payment_method: str = Field(
        ...,
        pattern="^(cash|card|online)$",
        description="Invalid payment method",
    )
    comment: Optional[str] = Field(default=None, max_length=500)

    @field_validator("first_name", "last_name", "patronymic")
    @classmethod
    def validate_name_fields(cls, value):
        if value is None:
            return value
        if value.strip() == "":
            raise ValueError("Name field cannot be empty or whitespace only")
        return value.title()


class BaseOrderSchema(OrderFields):
    id: int = Field(..., description="Order ID")  # noqa
    status: str = Field(
        ...,
        pattern="^(pending|processing|shipped|delivered|cancelled)$",
        description="Invalid order status",
    )
    waybill_number: Optional[str] = Field(None, max_length=30)
    created_at: datetime
    updated_at: datetime
    price_discount: float = Field(0, ge=0)
    is_paid: bool = Field(default=False)
    internal_comment: Optional[str] = Field(default=None, max_length=500)


class ReadOrderBaseSchema(BaseOrderSchema):
    pass


class ReadOrderSchema(BaseOrderSchema):
    items: list[ReadOrderItemSchema]


class ReadExtendedOrderSchema(ReadOrderSchema):
    total_price: float = Field(..., ge=0, description="Non-negative value")
    total_quantity: int = Field(..., ge=0, description="Non-negative value")


class CreateOrderSchema(OrderFields):
    pass


class CreateOrderWithUserSchema(OrderFields, UserIdField):
    pass


class UpdateOrderSchema(BaseModel):
    status: Optional[str] = Field(
        default=None,
        pattern="^(pending|processing|shipped|delivered|cancelled)$",
        description="Invalid order status",
    )
    waybill_number: Optional[str] = Field(None, max_length=30)
    price_discount: Optional[float] = Field(None, ge=0)
    is_paid: Optional[bool] = Field(default=None)

    first_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="First Name",
        pattern=r"^[\p{L}' -]+$",
    )
    last_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Last Name",
        pattern=r"^[\p{L}' -]+$",
    )
    patronymic: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        title="Patronymic",
        pattern=r"^[\p{L}' -]+$",
    )
    phone_number: Optional[str] = Field(
        default=None,
        min_length=9,
        max_length=19,
        title="Phone Number",
        pattern=r"^\d{9,19}$",
    )
    email: Optional[EmailStr] = Field(
        default=None,
        min_length=5,
        max_length=255,
        title="Email address of the user",
    )
    address: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=200,
        description="5-200 characters",
    )
    shipping_method: Optional[str] = Field(
        default=None,
        pattern="^(nova_poshta|ukrposhta|courier)$",
        description="Invalid shipping method",
    )
    payment_method: Optional[str] = Field(
        default=None,
        pattern="^(cash|card|online)$",
        description="Invalid payment method",
    )
    comment: Optional[str] = Field(default=None, max_length=500)
    internal_comment: Optional[str] = Field(default=None, max_length=500)

    @field_validator("first_name", "last_name", "patronymic")
    @classmethod
    def validate_name_fields(cls, value):
        if value is None:
            return value
        if value.strip() == "":
            raise ValueError("Name field cannot be empty or whitespace only")
        return value.title()


class ReadCustomerSchema(BaseModel):
    phone_number: str = Field(min_length=9, max_length=19, pattern=r"^\d{9,19}$")
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    patronymic: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    is_registered: bool = False
    orders_count: int = Field(ge=0)
    total_spent: float = Field(ge=0)
    last_order_at: datetime
