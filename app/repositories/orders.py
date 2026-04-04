import logging
from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload

from app.models.orders import Order, OrderItem
from app.models.products import ProductVariation
from app.utils.sql_repository import BaseRepository


logger = logging.getLogger(__name__)


# TODO: better typing
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
            .order_by(self.model.created_at.desc())  # TODO: hardcoded
        )

    async def all(  # noqa
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ):
        query = await self._apply_listing(
            self._get_base_query(),
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            options=options,
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    # TODO: do 1 method with some enum flag
    async def finished_orders_by_user_id(self, user_id: int):
        stmt = self._get_base_query().where(
            and_(
                self.model.user_id == user_id,
                self.model.status.in_(["delivered", "cancelled"]),
            ),
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def current_orders_by_user_id(self, user_id: int):
        stmt = self._get_base_query().where(
            and_(
                self.model.user_id == user_id,
                self.model.status.notin_(["delivered", "cancelled"]),
            ),
        )
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()
