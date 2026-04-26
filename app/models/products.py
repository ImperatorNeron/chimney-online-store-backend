from typing import Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin


if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.categories import Category
    from app.models.likes import Like
    from app.models.orders import OrderItem
    from app.models.product_images import ProductImage


class UniqueProduct(BaseModel, IdIntPkMixin, UpdateCreateDateTimeMixin):
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    variations: Mapped[list["ProductVariation"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductVariation(BaseModel, IdIntPkMixin, UpdateCreateDateTimeMixin):

    __table_args__ = (
        CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="discount_range",
        ),
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("uniqueproducts.id", ondelete="CASCADE"),
        nullable=False,
    )
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_percentage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )

    diameter: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    length: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    thickness: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    angle: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    metal_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    extra_attrs: Mapped[dict] = mapped_column(JSONB, nullable=True)

    product: Mapped[UniqueProduct] = relationship(back_populates="variations")
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
