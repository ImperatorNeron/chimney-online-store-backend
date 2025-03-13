from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin
from app.schemas.products import ProductImageRead, ReadFullProductSchema, ReadPreviewProductSchema, ReadProductSchema


if TYPE_CHECKING:
    from app.models.categories import Category


class ProductImage(BaseModel, IdIntPkMixin):

    file_path: Mapped[str] = mapped_column(String(512))
    alt: Mapped[str] = mapped_column(String(200))
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
    )

    product: Mapped["Product"] = relationship(back_populates="images")

    def to_read_model(self):
        return ProductImageRead(
            id=self.id,
            alt=self.alt,
            file_path=self.file_path,
            product_id=self.product_id,
        )

    def __repr__(self):
        return f"<ProductImage(id={self.id}, file_path='{self.file_path}', product_id={self.product_id})>"


class Product(BaseModel, IdIntPkMixin, UpdateCreateDateTimeMixin):
    name: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(back_populates="products")
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
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
            category_id=self.category_id,
            images=images_schemas,
        )

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
