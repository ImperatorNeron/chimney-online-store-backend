from datetime import datetime, timedelta
from typing import Optional

from app.models.messages import Message
from app.utils.search_mixin import RelevanceSearchMixin
from app.utils.sql_repository import BaseRepository


class MessageRepository(RelevanceSearchMixin, BaseRepository):
    """Repository for performing CRUD operations on Message data."""

    model = Message
    search_ilike_fields = [Message.user_name, Message.phone_number, Message.message]
    search_similarity_fields = [Message.message]
    search_similarity_threshold = 0.7

    def _apply_filters(self, query, filters: Optional[dict] = None):
        if not filters:
            return query

        if filters.get("id") is not None:
            return super()._apply_filters(query=query, filters=filters)

        if filters.get("status") is not None:
            query = query.where(self.model.status == filters.get("status"))

        if filters.get("text"):
            query = self._apply_relevance_filter(query, filters["text"])

        if filters.get("date_from"):
            date_from = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            query = query.where(self.model.created_at >= date_from)

        if filters.get("date_to"):
            date_to = datetime.strptime(filters["date_to"], "%Y-%m-%d") + timedelta(days=1)
            query = query.where(self.model.created_at < date_to)

        return query

    def _apply_ordering(self, query, order_by: list[str]):
        query = self._apply_relevance_ordering(query)
        return super()._apply_ordering(query, order_by)
