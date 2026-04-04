from app.models.likes import Like
from app.utils.sql_repository import BaseRepository


class LikeRepository(BaseRepository):
    """Repository for performing CRUD operations on Like data."""

    model = Like
