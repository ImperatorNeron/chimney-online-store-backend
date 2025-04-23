from app.models.orders import OrderItem
from app.schemas.orders import CreateOrderItemSchema, ReadOrderItemBaseSchema
from app.utils.sql_repository import BaseRepository


class OrderItemRepository(BaseRepository):
    """Repository for performing CRUD operations on OrderItem data."""

    model = OrderItem

    async def bulk_create(
        self,
        data_list: list[CreateOrderItemSchema],
    ) -> list[ReadOrderItemBaseSchema]:
        instances = [self.model(**data.model_dump()) for data in data_list]
        self.session.add_all(instances)
        await self.session.flush(instances)
        return [instance.to_read_base_model() for instance in instances]
