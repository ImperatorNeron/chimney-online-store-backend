import re

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin


class FAQ(BaseModel, IdIntPkMixin):
    question: Mapped[str] = mapped_column(String(255))
    answer: Mapped[str] = mapped_column(Text)
    youtube_url: Mapped[str] = mapped_column(Text, nullable=True)

    def get_embed_url(self):
        if not self.youtube_url:
            return None
        pattern = (
            r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([^\s&]+)"
        )
        match = re.match(pattern, self.youtube_url)
        if match:
            video_id = match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        return None
