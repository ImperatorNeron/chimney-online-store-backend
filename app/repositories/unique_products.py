from app.models.products import UniqueProduct
from app.utils.sql_repository import BaseRepository


class UniqueProductRepository(BaseRepository):
    """Repository for performing CRUD operations on UniqueProduct data."""

    model = UniqueProduct
