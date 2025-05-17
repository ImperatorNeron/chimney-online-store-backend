from typing import Optional

from sqlalchemy.orm import selectinload

from app.models.products import UniqueProduct
from app.utils.sql_repository import BaseRepository


class UniqueProductRepository(BaseRepository):
    """Repository for performing CRUD operations on UniqueProduct data."""

    model = UniqueProduct
    default_preload = [selectinload(UniqueProduct.images)]

    async def all(  # noqa
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        models = await self._all_models(
            limit=limit,
            offset=offset,
            options=self.default_preload,
        )
        return [model.to_read_full_model() for model in models]
