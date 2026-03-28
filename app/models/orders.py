from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin
from app.models.products import ProductVariation


class Order(BaseModel, IdIntPkMixin, UpdateCreateDateTimeMixin):
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    patronymic: Mapped[str | None] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(320))
    address: Mapped[str] = mapped_column(String(200))
    waybill_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=True)
    price_discount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        default=0,
        server_default="0",
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
        default="pending",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete",
    )


class OrderItem(BaseModel, IdIntPkMixin):
    __table_args__ = (
        UniqueConstraint(
            "order_id",
            "product_id",
            name="uq_orderitems_order_id_product_id",
        ),
    )
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("productvariations.id"))

    quantity: Mapped[int] = mapped_column(Integer)
    price_at_order: Mapped[float] = mapped_column(Numeric(10, 2))
    order: Mapped[Order] = relationship("Order", back_populates="items")
    product: Mapped["ProductVariation"] = relationship(
        "ProductVariation",
        back_populates="order_items",
    )
