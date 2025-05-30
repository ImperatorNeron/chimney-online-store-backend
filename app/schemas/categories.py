from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.validators import SlugValidatorMixin


class BaseCategorySchema(BaseModel, SlugValidatorMixin):
    name: str = Field(..., min_length=5, max_length=150, example="Одностінні труби")
    slug: str = Field(..., min_length=5, max_length=255, example="odnostinni-trybu")
    file_path: Optional[str] = Field(None, max_length=512)
    parent_id: Optional[int] = Field(None, ge=0, example=0)


class ReadCategorySchema(BaseCategorySchema):
    id: int = Field(ge=0)  # noqa


class CreateCategorySchema(BaseCategorySchema):
    pass


class UpdateCategorySchema(BaseModel, SlugValidatorMixin):
    name: Optional[str] = Field(
        None,
        min_length=5,
        max_length=150,
        example="Одностінні труби",
    )
    slug: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255,
        example="odnostinni-trybu",
    )
    file_path: Optional[str] = Field(None, max_length=512)
    parent_id: Optional[int] = Field(None, ge=0, example=0)
