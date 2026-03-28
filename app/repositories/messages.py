from typing import Optional

from sqlalchemy import func, or_

from app.models.messages import Message
from app.utils.sql_repo import BaseRepository


class MessageRepository(BaseRepository):
    """Repository for performing CRUD operations on Message data."""

    model = Message

    def _apply_filters(self, query, filters: Optional[dict] = None):
        if not filters:
            return query

        if filters.get("id") is not None:
            return super()._apply_filters(query=query, filters=filters)

        if filters.get("status") is not None:
            query = query.where(self.model.status == filters.get("status"))

        if filters.get("text"):
            search_terms = filters.get("text").split()
            conditions = []

            for term in search_terms:
                conditions.append(self.model.user_name.ilike(f"%{term}%"))
                conditions.append(self.model.phone_number.ilike(f"%{term}%"))
                conditions.append(func.similarity(self.model.message, term) >= 0.1)

            query = query.where(or_(*conditions))

        return query
