from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import backref, Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin
from app.schemas.categories import ReadCategorySchema


if TYPE_CHECKING:
    from app.models.products import UniqueProduct


class Category(BaseModel, IdIntPkMixin):
    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    products: Mapped[list["UniqueProduct"]] = relationship(
        "UniqueProduct",
        back_populates="category",
        cascade="all, delete",
    )

    children = relationship(
        "Category",
        cascade="all, delete",
        lazy="dynamic",
        backref=backref("parent", remote_side="[Category.id]"),
    )

    __table_args__ = (
        UniqueConstraint("name", "parent_id", name="uix_category_parent_name"),
    )

    def to_read_model(self):
        return ReadCategorySchema(
            id=self.id,
            name=self.name,
            slug=self.slug,
            file_path=self.file_path,
            parent_id=self.parent_id,
        )

    def __repr__(self):
        return (
            f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
        )
