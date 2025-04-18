from typing import Optional

from pydantic import BaseModel, Field


class YoutubeUrlField(BaseModel):
    youtube_url: Optional[str] = Field(
        default=None,
        example="https://www.youtube.com/watch?v=-yIsQPp31L0&ab_channel=ByteGrad",
    )


class BaseFAQSchema(BaseModel):
    question: str = Field(..., max_length=255, example="Як скинути пароль?")
    answer: str = Field(..., example="Перейдіть до налаштувань...")


class ReadFAQSchema(BaseFAQSchema, YoutubeUrlField):
    id: int  # noqa
    embed_url: Optional[str] = Field(
        default=None,
        example="https://www.youtube.com/embed/dQw4w9WgXcQ",
    )


class CreateFAQSchema(BaseFAQSchema, YoutubeUrlField):
    pass


class UpdadeFAQSchema(YoutubeUrlField):
    question: Optional[str] = Field(
        default=None,
        max_length=255,
        example="Як скинути пароль?",
    )
    answer: Optional[str] = Field(default=None, example="Перейдіть до налаштувань...")
