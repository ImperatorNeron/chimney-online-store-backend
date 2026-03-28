from app.models.likes import Like
from app.utils.sql_repo import BaseRepository


class LikeRepository(BaseRepository):
    """Repository for performing CRUD operations on Like data."""

    model = Like
