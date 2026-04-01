from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from app.models.products import UniqueProduct
from app.utils.sql_repo import BaseRepository


class UniqueProductRepository(BaseRepository):
    """Repository for performing CRUD operations on UniqueProduct data."""

    model = UniqueProduct
    all_models_default_preload = [selectinload(UniqueProduct.images)]

    def _apply_filters(self, query, filters: Optional[dict] = None):

        cleaned = {k: v for k, v in filters.items() if v is not None}

        if cleaned.get("text"):
            search_terms = cleaned.get("text").split()
            conditions = []

            for term in search_terms:
                conditions.append(self.model.slug.ilike(f"%{term}%"))
                conditions.append(func.similarity(self.model.name, term) >= 0.1)

            query = query.where(or_(*conditions))
            cleaned.pop("text")

        if not cleaned:
            return query

        return super()._apply_filters(query=query, filters=cleaned)
