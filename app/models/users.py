from typing import TYPE_CHECKING

from sqlalchemy import Boolean, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin


if TYPE_CHECKING:
    from app.models.likes import Like


class User(
    IdIntPkMixin,
    UpdateCreateDateTimeMixin,
    BaseModel,
):
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )
    phone_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=True,
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=True,
    )
    hashed_password: Mapped[bytes] = mapped_column(
        LargeBinary,
    )
    first_name: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )
    patronymic: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )

    likes: Mapped[list["Like"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
