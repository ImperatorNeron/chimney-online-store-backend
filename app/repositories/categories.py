from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.models.categories import Category
from app.utils.sql_repository import BaseRepository


class CategoryRepository(BaseRepository):
    """Repository for performing CRUD operations on Categories data."""

    model = Category

    async def get_category_hierarchy(self, category_id: int) -> list[list[str, str]]:
        parent_alias = aliased(self.model)
        cte = (
            select(
                self.model.id, self.model.name, self.model.slug, self.model.parent_id,
            )
            .where(self.model.id == category_id)
            .cte(name="category_cte", recursive=True)
        )
        cte_alias = aliased(cte)

        cte = cte.union_all(
            select(
                parent_alias.id,
                parent_alias.name,
                parent_alias.slug,
                parent_alias.parent_id,
            ).where(parent_alias.id == cte_alias.c.parent_id),
        )

        query = select(cte.c.id, cte.c.name, cte.c.slug)
        result = await self.session.execute(query)
        rows = result.all()
        return [(row.name, row.slug) for row in rows]

    async def get_category_names_from_slugs(
        self,
        slugs: list[str],
    ) -> list[list[str, str]]:
        if not slugs:
            return []

        query = select(self.model.name, self.model.slug).where(Category.slug.in_(slugs))
        result = await self.session.execute(query)
        rows = result.all()
        return [[name, slug] for name, slug in rows]
