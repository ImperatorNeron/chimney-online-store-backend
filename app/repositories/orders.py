from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from app.core.exceptions.common import RepositoryException
from app.models.orders import Order, OrderItem
from app.schemas.orders import CreateOrderSchema
from app.utils.sql_repository import BaseRepository


class OrderRepository(BaseRepository):
    """Repository for performing CRUD operations on Order data."""

    model = Order

    async def all(self):  # noqa
        stmt = select(self.model).options(
            joinedload(Order.items).joinedload(OrderItem.product),
        )
        result = await self.session.execute(stmt)
        orders = result.unique().scalars().all()
        return [order.to_read_model() for order in orders]

    async def create(self, order_in: CreateOrderSchema):
        try:
            stmt = (
                insert(self.model).values(**order_in.model_dump()).returning(self.model)
            )
            result = await self.session.execute(stmt)
            instance = result.scalar_one()
            return instance.to_read_model_without_items()
        except Exception as e:
            print(e)
            raise RepositoryException()
