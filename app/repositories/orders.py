import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import joinedload

from app.core.exceptions.common import ItemNotFoundException
from app.models.orders import Order, OrderItem
from app.models.products import ProductVariation
from app.models.users import User
from app.utils.sql_repository import BaseRepository


logger = logging.getLogger(__name__)


# TODO: better typing
class OrderRepository(BaseRepository):
    """Repository for performing CRUD operations on Order data."""

    model = Order

    _custom_filter_keys = {"text", "status", "shipping_method", "payment_method", "date_from", "date_to"}

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
                conditions.append(self.model.email.ilike(f"%{term}%"))
                if term.isdigit():
                    conditions.append(self.model.id == int(term))
                if len(term) >= 3:
                    conditions.append(self.model.phone_number.ilike(f"%{term}%"))

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

        remaining = {k: v for k, v in filters.items() if k not in self._custom_filter_keys and v is not None}
        if remaining:
            query = super()._apply_filters(query, remaining)

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
    async def finished_orders_by_user_id(self, user_id: int, limit: int = None, offset: int = None):
        stmt = self._get_base_query().where(
            and_(
                self.model.user_id == user_id,
                self.model.status.in_(["delivered", "cancelled"]),
            ),
        ).order_by(self.model.created_at.desc())
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def current_orders_by_user_id(self, user_id: int, limit: int = None, offset: int = None):
        stmt = self._get_base_query().where(
            and_(
                self.model.user_id == user_id,
                self.model.status.notin_(["delivered", "cancelled"]),
            ),
        ).order_by(self.model.created_at.desc())
        if limit:
            stmt = stmt.limit(limit)
        if offset:
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def get_with_items(self, order_id: int):
        stmt = self._get_base_query().where(self.model.id == order_id)
        result = await self.session.execute(stmt)
        order = result.unique().scalars().first()
        if not order:
            raise ItemNotFoundException()
        return order

    async def get_customers(
        self, limit: int = 20, offset: int = 0,
        order_by: str = "last_order_at", ordering: str = "desc",
        text: str = None, is_registered: str = None, date_from: str = None, date_to: str = None,
    ) -> list:
        query = self._customers_base_query(text)
        query = self._apply_customer_filters(query, is_registered, date_from, date_to)

        order_fields = {
            "last_order_at": func.max(self.model.created_at),
            "first_name": func.coalesce(func.max(User.first_name), func.max(self.model.first_name)),
            "last_name": func.coalesce(func.max(User.last_name), func.max(self.model.last_name)),
            "patronymic": func.coalesce(func.max(User.patronymic), func.max(self.model.patronymic)),
            "email": func.coalesce(func.max(User.email), func.max(self.model.email)),
            "orders_count": func.count(func.distinct(self.model.id)),
            "total_spent": func.coalesce(func.sum(OrderItem.price_at_order), 0),
            "phone_number": self.model.phone_number,
            "is_registered": func.max(self.model.user_id),
        }
        field = order_fields.get(order_by, order_fields["last_order_at"])
        query = query.order_by(field.desc() if ordering == "desc" else field.asc())
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.all()

    async def get_customers_count(
            self,
            text: str = None,
            is_registered: str = None,
            date_from: str = None,
            date_to: str = None,
    ) -> int:
        query = self._customers_base_query(text)
        query = self._apply_customer_filters(query, is_registered, date_from, date_to)
        subq = query.subquery()
        return (await self.session.execute(select(func.count()).select_from(subq))).scalar_one()

    def _customers_base_query(self, text: str = None):
        query = (
            select(
                self.model.phone_number,
                func.coalesce(func.max(User.first_name), func.max(self.model.first_name)).label("first_name"),
                func.coalesce(func.max(User.last_name), func.max(self.model.last_name)).label("last_name"),
                func.coalesce(func.max(User.patronymic), func.max(self.model.patronymic)).label("patronymic"),
                func.coalesce(func.max(User.email), func.max(self.model.email)).label("email"),
                func.max(self.model.user_id).label("user_id"),
                func.count(func.distinct(self.model.id)).label("orders_count"),
                func.coalesce(func.sum(OrderItem.price_at_order), 0).label("total_spent"),
                func.max(self.model.created_at).label("last_order_at"),
            )
            .outerjoin(OrderItem, OrderItem.order_id == self.model.id)
            .outerjoin(User, User.phone_number == self.model.phone_number)
            .group_by(self.model.phone_number)
        )
        if text:
            term = f"%{text}%"
            query = query.having(
                or_(
                    func.coalesce(func.max(User.first_name), func.max(self.model.first_name)).ilike(term),
                    func.coalesce(func.max(User.last_name), func.max(self.model.last_name)).ilike(term),
                    func.coalesce(func.max(User.patronymic), func.max(self.model.patronymic)).ilike(term),
                    self.model.phone_number.ilike(term),
                    func.coalesce(func.max(User.email), func.max(self.model.email)).ilike(term),
                ),
            )
        return query

    def _apply_customer_filters(self, query, is_registered: str = None, date_from: str = None, date_to: str = None):
        if is_registered == "true":
            query = query.having(func.max(self.model.user_id) != None)  # noqa
        elif is_registered == "false":
            query = query.having(func.max(self.model.user_id) == None)  # noqa

        if date_from:
            d = datetime.strptime(date_from, "%Y-%m-%d")
            query = query.having(func.max(self.model.created_at) >= d)

        if date_to:
            d = datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            query = query.having(func.max(self.model.created_at) < d)

        return query
