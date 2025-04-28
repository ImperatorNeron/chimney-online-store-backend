from sqlalchemy import and_, insert, select
from sqlalchemy.orm import joinedload

from app.core.exceptions.common import RepositoryException
from app.models.orders import Order, OrderItem
from app.models.products import ProductVariation
from app.schemas.orders import CreateOrderSchema
from app.utils.sql_repository import BaseRepository


class OrderRepository(BaseRepository):
    """Repository for performing CRUD operations on Order data."""

    model = Order

    def _get_base_query(self):
        return (
            select(self.model)
            .options(
                joinedload(self.model.items)
                .joinedload(OrderItem.product)
                .joinedload(ProductVariation.product),
            )
            .order_by(self.model.created_at.desc())
        )

    async def all(self):  # noqa
        result = await self.session.execute(self._get_base_query())
        orders = result.unique().scalars().all()
        return [order.to_read_model() for order in orders]

    async def finished_orders_by_user_id(self, user_id: int):
        stmt = self._get_base_query().where(
            and_(
                self.model.user_id == user_id,
                self.model.status.in_(["delivered", "cancelled"]),
            ),
        )
        result = await self.session.execute(stmt)
        orders = result.unique().scalars().all()
        return [order.to_read_model() for order in orders]

    async def current_orders_by_user_id(self, user_id: int):
        stmt = self._get_base_query().where(
            and_(
                self.model.user_id == user_id,
                self.model.status.notin_(["delivered", "cancelled"]),
            ),
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
