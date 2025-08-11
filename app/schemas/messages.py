import re
from datetime import datetime
from typing import Optional

from markupsafe import escape
from pydantic import BaseModel, Field, field_validator


class BaseMessageSchema(BaseModel):
    user_name: str = Field(
        min_length=2,
        max_length=50,
        title="Name of the user",
        example="Іван",
    )
    phone_number: str = Field(
        min_length=9,
        max_length=11,
        title="Phone number of the user",
        example="0991234567",
    )
    message: Optional[str] = Field(
        None,
        max_length=1000,
        title="Message from the user",
        example="Привіт!",
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str):
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        return value

    @field_validator("user_name")
    @classmethod
    def validate_user_name(cls, value: str):
        allowed_pattern = r"^[a-zA-Zа-яА-ЯїЇіІєЄґҐ'`\s-]+$"
        if not re.match(allowed_pattern, value):
            raise ValueError(
                "Name can only contain letters, spaces, apostrophes, and hyphens",
            )
        return value

    @field_validator("message")
    @classmethod
    def escape_html(cls, value):
        return escape(value)


class ReadMessageSchema(BaseMessageSchema):
    id: int  # noqa
    created_at: datetime = Field(title="Timestamp when the message was created")
    status: str = Field(title="Поточний статус", default="new")


class CreateMessageSchema(BaseMessageSchema):
    pass


class ChangeMessageStatusSchema(BaseModel):
    status: str = Field(title="Поточний статус", default="new")
