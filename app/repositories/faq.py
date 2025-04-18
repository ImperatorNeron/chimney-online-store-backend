from app.models.faq import FAQ
from app.utils.sql_repository import BaseRepository


class FAQRepository(BaseRepository):
    """Repository for performing CRUD operations on FAQ data."""

    model = FAQ
