from app.models.messages import Message
from app.utils.sql_repository import BaseRepository


class MessageRepository(BaseRepository):
    """Repository for performing CRUD operations on Message data."""

    model = Message
