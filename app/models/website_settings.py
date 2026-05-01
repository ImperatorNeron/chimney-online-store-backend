from typing import Optional

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class WebSiteSettings(BaseModel):
    __tablename__ = "website_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)  # noqa
    manufacturer_discount: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, server_default="0",
    )
    seller_markup: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, server_default="0",
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    work_schedule: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    telegram_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    facebook_url: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
