from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin


if TYPE_CHECKING:
    from app.models.cart_item import CartItem


class Cart(IdIntPkMixin, BaseModel):

    __table_args__ = (
        CheckConstraint(
            "user_id IS NOT NULL OR session_id IS NOT NULL",
            name="ck_cart_user_or_session",
        ),
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        unique=True,
    )
    session_id: Mapped[str] = mapped_column(String(47), nullable=True, unique=True)
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete",
    )
