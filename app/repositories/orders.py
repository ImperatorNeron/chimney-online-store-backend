import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import joinedload

from app.models.orders import Order, OrderItem
from app.models.products import ProductVariation
from app.utils.sql_repository import BaseRepository


logger = logging.getLogger(__name__)


# TODO: better typing
class OrderRepository(BaseRepository):
    """Repository for performing CRUD operations on Order data."""

    model = Order

    def _apply_filters(self, query, filters: Optional[dict] = None):
        if not filters:
            return query

        if filters.get("id") is not None:
            return super()._apply_filters(query=query, filters=filters)

        if filters.get("text"):
            search_terms = str(filters.get("text")).split()
            conditions = []

            for term in search_terms:
                conditions.append(self.model.first_name.ilike(f"%{term}%"))
                conditions.append(self.model.last_name.ilike(f"%{term}%"))
                conditions.append(self.model.patronymic.ilike(f"%{term}%"))
                conditions.append(self.model.phone_number.ilike(f"%{term}%"))
                conditions.append(self.model.email.ilike(f"%{term}%"))

            query = query.where(or_(*conditions))

        for field in ("status", "shipping_method", "payment_method"):
            if filters.get(field):
                query = query.where(getattr(self.model, field) == filters[field])

        if filters.get("date_from"):
            date_from = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            query = query.where(self.model.created_at >= date_from)

        if filters.get("date_to"):
            date_to = datetime.strptime(filters["date_to"], "%Y-%m-%d") + timedelta(days=1)
            query = query.where(self.model.created_at < date_to)

        return query

    def _get_base_query(self):
        return (
            select(self.model)
            .options(
                joinedload(self.model.items)
                .joinedload(OrderItem.product)
                .joinedload(ProductVariation.product),
            )
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
