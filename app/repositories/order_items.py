from app.models.orders import OrderItem
from app.schemas.orders import ReadOrderItemBaseSchema
from app.utils.sql_repository import BaseRepository


class OrderItemRepository(BaseRepository):
    """Repository for performing CRUD operations on OrderItem data."""

    model = OrderItem

    async def bulk_create(
        self,
        instances: list[OrderItem],
    ) -> list[ReadOrderItemBaseSchema]:
        self.session.add_all(instances)
        await self.session.flush(instances)
        return instances
