from app.models.products import Product
from app.utils.sql_repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on Product data."""

    model = Product
