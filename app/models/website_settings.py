from sqlalchemy import Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class WebSiteSettings(BaseModel):
    __tablename__ = "website_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1) # noqa
    manufacturer_discount: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, server_default="0",
    )
    seller_markup: Mapped[float] = mapped_column(
        Numeric(5, 2), default=0, server_default="0",
    )
