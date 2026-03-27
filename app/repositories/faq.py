from app.models.faq import FAQ
from app.utils.sql_repo import BaseRepository


class FAQRepository(BaseRepository):
    """Repository for performing CRUD operations on FAQ data."""

    model = FAQ
