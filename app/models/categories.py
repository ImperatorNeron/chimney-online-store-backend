from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin
from app.schemas.categories import ReadCategorySchema


class Category(BaseModel, IdIntPkMixin):
    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    def to_read_model(self):
        return ReadCategorySchema(
            id=self.id,
            name=self.name,
            slug=self.slug,
        )
