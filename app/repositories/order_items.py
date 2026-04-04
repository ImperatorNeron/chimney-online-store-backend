from app.models.orders import OrderItem
from app.utils.sql_repository import BaseRepository


class OrderItemRepository(BaseRepository):
    """Repository for performing CRUD operations on OrderItem data."""

    model = OrderItem
