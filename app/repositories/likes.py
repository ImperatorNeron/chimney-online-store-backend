from sqlalchemy import select, Sequence
from sqlalchemy.orm import selectinload

from app.models.likes import Like
from app.models.products import ProductVariation, UniqueProduct
from app.utils.sql_repository import BaseRepository


class LikeRepository(BaseRepository):
    """Repository for performing CRUD operations on Like data."""

    model = Like

    async def get_liked_products(
        self, user_id: int, limit: int = 20, offset: int = 0,
    ) -> Sequence[ProductVariation]:
        stmt = (
            select(ProductVariation)
            .join(Like, Like.product_id == ProductVariation.id)
            .where(Like.user_id == user_id)
            .options(selectinload(ProductVariation.product).selectinload(UniqueProduct.images))
            .order_by(Like.id.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
