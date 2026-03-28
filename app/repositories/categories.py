from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.models.categories import Category
from app.utils.sql_repo import BaseRepository


class CategoryRepository(BaseRepository):
    """Repository for performing CRUD operations on Categories data."""

    model = Category

    async def get_category_hierarchy(self, category_id: int) -> list[Category]:
        parent_alias = aliased(self.model)
        cte = (
            select(self.model)
            .where(self.model.id == category_id)
            .cte(name="category_cte", recursive=True)
        )
        cte_alias = aliased(cte)

        cte = cte.union_all(
            select(parent_alias).where(parent_alias.id == cte_alias.c.parent_id),
        )

        result = await self.session.execute(select(cte.c))
        return result.all()

    async def get_category_names_from_slugs(
        self,
        slugs: list[str],
    ) -> Sequence[Category]:
        return await self.all(filters={"slug__in": slugs})

    async def get_children_by_parent_ids(
        self,
        parent_ids: list[int],
    ):
        return await self.all(filters={"parent_id__in": parent_ids})
