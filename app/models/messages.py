from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.models.mixins import CreateDateTimeMixin, IdIntPkMixin


class Message(IdIntPkMixin, CreateDateTimeMixin, BaseModel):
    user_name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(10), server_default="new", default="new")
