from typing import Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin
from app.schemas.products import (
    ReadFullProductSchema,
    ReadFullUniqueProductSchema,
    ReadPreviewProductSchema,
    ReadProductSchema,
    ReadProductVariationSchema,
    ReadUniqueProductSchema,
)


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

    def to_read_model(self):
        return ReadUniqueProductSchema(
            id=self.id,
            name=self.name,
            slug=self.slug,
            description=self.description,
            category_id=self.category_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_read_full_model(self):
        images_schemas = [image.to_read_model() for image in self.images]
        return ReadFullUniqueProductSchema(
            **self.to_read_model().model_dump(), images=images_schemas,
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
    metal_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    extra_attrs: Mapped[dict] = mapped_column(JSONB, nullable=True)

    product: Mapped[UniqueProduct] = relationship(back_populates="variations")
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def _get_common_fields(self) -> dict:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "name": self.product.name,
            "slug": self.product.slug,
            "description": self.product.description,
            "price": self.price,
            "discount_price": round(
                self.price - self.price * self.discount_percentage / 100,
                2,
            ),
            "discount_percentage": self.discount_percentage,
            "category_id": self.product.category_id,
            "extra_attrs": self.extra_attrs,
            "diameter": self.diameter,
            "length": self.length,
            "thickness": self.thickness,
            "angle": self.angle,
            "metal_type": self.metal_type,
        }

    def to_read_model(self):
        return ReadProductSchema(**self._get_common_fields())

    def to_read_base_model(self):
        return ReadProductVariationSchema(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            discount_price=self.price - (self.price * self.discount_percentage) / 100,
            discount_percentage=self.discount_percentage,
            diameter=self.diameter,
            length=self.length,
            thickness=self.thickness,
            angle=self.angle,
            metal_type=self.metal_type,
        )

    def to_read_model_with_preview(self):
        preview_image = (
            self.product.images[0].to_read_model() if self.product.images else None
        )
        return ReadPreviewProductSchema(
            **self._get_common_fields(),
            preview=preview_image,
        )

    def to_read_full_model(self):
        images_schemas = [image.to_read_model() for image in self.product.images]
        return ReadFullProductSchema(**self._get_common_fields(), images=images_schemas)
