from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin


if TYPE_CHECKING:
    from app.models.products import ProductVariation
    from app.models.users import User


class Like(BaseModel, IdIntPkMixin):

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("productvariations.id", ondelete="CASCADE"),
    )

    user: Mapped["User"] = relationship(back_populates="likes")
    product: Mapped["ProductVariation"] = relationship(back_populates="likes")

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_like_user_id_product_id"),
    )
