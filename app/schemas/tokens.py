from pydantic import BaseModel

from app.core.settings import settings


class TokenInfoSchema(BaseModel):
    access_token: str
    access_token_expire_seconds: int = (settings.auth_jwt.access_token_expire_minutes - 1) * 60
    token_type: str = "Bearer"
