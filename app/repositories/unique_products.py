from typing import Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload

from app.models.products import UniqueProduct
from app.utils.sql_repository import BaseRepository


class UniqueProductRepository(BaseRepository):
    """Repository for performing CRUD operations on UniqueProduct data."""

    model = UniqueProduct
    default_preload = [selectinload(UniqueProduct.images)]

    async def all(  # noqa
        self,
        order_by: Optional[list] = None,
        filters: Optional[dict] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        models = await self._all_models(
            limit=limit,
            offset=offset,
            order_by=order_by,
            filters=filters,
            options=self.default_preload,
        )
        return [model.to_read_full_model() for model in models]

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
