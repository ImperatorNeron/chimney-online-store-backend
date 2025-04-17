from sqlalchemy import Boolean, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.models.mixins import IdIntPkMixin, UpdateCreateDateTimeMixin
from app.schemas.users import ReadUserWithPasswordSchema


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

    def to_read_model(self):
        return ReadUserWithPasswordSchema(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            email=self.email,
            phone_number=self.phone_number,
            username=self.username,
            is_verified=self.is_verified,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            hashed_password=self.hashed_password,
            first_name=self.first_name,
            last_name=self.last_name,
            patronymic=self.patronymic,
        )
