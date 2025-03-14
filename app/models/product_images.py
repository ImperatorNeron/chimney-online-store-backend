from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin
from app.schemas.products import ProductImageRead


if TYPE_CHECKING:
    from app.models.products import Product


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
