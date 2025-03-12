from app.models.categories import Category
from app.utils.sql_repository import SQLAlchemyRepository


class CategoryRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on Categories data."""

    model = Category
