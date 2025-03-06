from app.models.base import BaseModel
from app.models.mixins import CreateDateTimeMixin, IdIntPkMixin

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.schemas.messages import ReadMessageSchema


class Message(IdIntPkMixin, CreateDateTimeMixin, BaseModel):
    user_name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(1000))

    def to_read_model(self):
        return ReadMessageSchema(
            id=self.id,
            user_name=self.user_name,
            phone_number=self.phone_number,
            message=self.message,
            created_at=self.created_at,
        )
