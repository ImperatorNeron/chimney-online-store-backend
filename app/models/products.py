from typing import Optional, TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin
from app.schemas.products import ReadFullProductSchema, ReadPreviewProductSchema, ReadProductSchema


if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.categories import Category
    from app.models.likes import Like
    from app.models.product_images import ProductImage


class Product(BaseModel, IdIntPkMixin, UpdateCreateDateTimeMixin):

    __table_args__ = (
        CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="discount_range",
        ),
    )

    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    discount_percentage: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=0,
        server_default="0",
    )
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(back_populates="products")
    items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    likes: Mapped[list["Like"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_read_model(self):
        return ReadProductSchema(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            slug=self.slug,
            description=self.description,
            price=self.price,
            discount_price=round(
                self.price - self.price * self.discount_percentage / 100,
                2,
            ),
            discount_percentage=self.discount_percentage,
            category_id=self.category_id,
        )

    def to_read_model_with_preview(self):

        preview_image = None
        if self.images:
            preview_image = self.images[0].to_read_model()

        return ReadPreviewProductSchema(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            slug=self.slug,
            description=self.description,
            price=self.price,
            discount_price=round(
                self.price - self.price * self.discount_percentage / 100,
                2,
            ),
            discount_percentage=self.discount_percentage,
            category_id=self.category_id,
            preview=preview_image,
        )

    def to_read_full_model(self):
        images_schemas = [image.to_read_model() for image in self.images]
        return ReadFullProductSchema(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            name=self.name,
            slug=self.slug,
            description=self.description,
            price=self.price,
            discount_price=round(
                self.price - self.price * self.discount_percentage / 100,
                2,
            ),
            discount_percentage=self.discount_percentage,
            category_id=self.category_id,
            images=images_schemas,
        )

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
