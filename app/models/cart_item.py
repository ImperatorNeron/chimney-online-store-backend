from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin
from app.schemas.cart_items import ReadCartItemSchema, ReadCartItemWithProductSchema


if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.products import ProductVariation


class CartItem(IdIntPkMixin, BaseModel):

    cart_id: Mapped[int] = mapped_column(Integer, ForeignKey("carts.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("productvariations.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items")
    product: Mapped["ProductVariation"] = relationship("ProductVariation", back_populates="cart_items")

    def to_read_model(self):
        return ReadCartItemSchema(
            id=self.id,
            cart_id=self.cart_id,
            quantity=self.quantity,
            product_id=self.product_id,
        )

    def to_read_model_with_product(self):
        return ReadCartItemWithProductSchema(
            id=self.id,
            cart_id=self.cart_id,
            quantity=self.quantity,
            product=self.product.to_read_model_with_preview(),
        )
