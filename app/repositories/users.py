from app.models.users import User
from app.utils.sql_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    """Repository for performing CRUD operations on User data."""

    model = User
