from app.models.product_images import ProductImage
from app.utils.sql_repo import BaseRepository


class ProductImageRepository(BaseRepository):
    """Repository for performing CRUD operations on ProductImages data."""

    model = ProductImage
