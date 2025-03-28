from app.models.categories import Category
from app.utils.sql_repository import BaseRepository


class CategoryRepository(BaseRepository):
    """Repository for performing CRUD operations on Categories data."""

    model = Category
