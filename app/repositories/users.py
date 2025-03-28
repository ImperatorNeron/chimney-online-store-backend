from app.models.users import User
from app.utils.sql_repository import BaseRepository


class UserRepository(BaseRepository):
    """Repository for performing CRUD operations on User data."""

    model = User
