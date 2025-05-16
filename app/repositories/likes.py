from app.models.likes import Like
from app.utils.sql_repository import BaseRepository


class LikeRepository(BaseRepository):
    """Repository for performing CRUD operations on Like data."""

    model = Like

    async def all(self, user_id: int):  # noqa
        models = await self._all_models(filters={"user_id": user_id})
        return [model.product_id for model in models]
