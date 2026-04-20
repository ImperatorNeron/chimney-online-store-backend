from typing import Optional

from sqlalchemy.orm import selectinload

from app.models.products import UniqueProduct
from app.utils.search_mixin import RelevanceSearchMixin
from app.utils.sql_repository import BaseRepository


class UniqueProductRepository(RelevanceSearchMixin, BaseRepository):
    """Repository for performing CRUD operations on UniqueProduct data."""

    model = UniqueProduct
    all_models_default_preload = [selectinload(UniqueProduct.images)]
    search_ilike_fields = [UniqueProduct.name, UniqueProduct.slug]
    search_similarity_fields = [UniqueProduct.name]
    search_similarity_threshold = 0.7

    def _apply_filters(self, query, filters: Optional[dict] = None):
        cleaned = {k: v for k, v in filters.items() if v is not None}

        if cleaned.get("text"):
            query = self._apply_relevance_filter(query, cleaned.pop("text"))

        if not cleaned:
            return query

        return super()._apply_filters(query=query, filters=cleaned)

    def _apply_ordering(self, query, order_by: list[str]):
        query = self._apply_relevance_ordering(query)
        return super()._apply_ordering(query, order_by)
