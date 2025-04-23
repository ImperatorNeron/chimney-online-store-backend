from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin
from app.models.products import Product
from app.schemas.orders import ReadOrderBaseSchema, ReadOrderItemBaseSchema, ReadOrderItemSchema, ReadOrderSchema


class Order(BaseModel, IdIntPkMixin, UpdateCreateDateTimeMixin):
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str | None] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(320))
    address: Mapped[str] = mapped_column(String(200))
    price_discount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, server_default="0",
    )

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    shipping_method: Mapped[str] = mapped_column(
        String(20),
        default="нова пошта",
    )
    payment_method: Mapped[str] = mapped_column(
        String(20),
        default="накладений платіж",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="обробляється",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    def to_read_model(self) -> ReadOrderSchema:
        data = {
            **self._get_base_fields(),
            "items": [item.to_read_model() for item in self.items],
        }
        return ReadOrderSchema(**data)

    def to_read_model_without_items(self) -> ReadOrderBaseSchema:
        return ReadOrderBaseSchema(**self._get_base_fields())

    def _get_base_fields(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "patronymic": self.patronymic,
            "phone_number": self.phone_number,
            "email": self.email,
            "address": self.address,
            "shipping_method": self.shipping_method,
            "payment_method": self.payment_method,
            "price_discount": (
                float(self.price_discount) if self.price_discount else 0.0
            ),
        }


class OrderItem(BaseModel, IdIntPkMixin):
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_id",
            name="uq_orderitems_order_id_product_id",
        ),
    )
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    quantity: Mapped[int] = mapped_column(Integer)
    price_at_order: Mapped[float] = mapped_column(Numeric(10, 2))
    order: Mapped[Order] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

    def to_read_model(self):
        return ReadOrderItemSchema(
            **self._get_base_fields(),
            product=self.product.to_read_model(),
        )

    def to_read_base_model(self):
        return ReadOrderItemBaseSchema(
            **self._get_base_fields(),
            product_id=self.product_id,
        )

    def _get_base_fields(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "quantity": self.quantity,
            "price_at_order": self.price_at_order,
        }
