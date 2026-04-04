from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin


if TYPE_CHECKING:
    from app.models.products import UniqueProduct


class ProductImage(BaseModel, IdIntPkMixin):

    file_path: Mapped[str] = mapped_column(String(512))
    alt: Mapped[str] = mapped_column(String(200))
    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "uniqueproducts.id",
            ondelete="CASCADE",
        ),
    )

    product: Mapped["UniqueProduct"] = relationship(back_populates="images")
