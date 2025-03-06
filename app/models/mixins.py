from datetime import datetime

from sqlalchemy import (
    DateTime,
    func,
    Integer,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)


class IdIntPkMixin:
    id: Mapped[int] = mapped_column(  # noqa
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )


class CreateDateTimeMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        server_default=func.now(),
    )


class UpdateDateTimeMixin:
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        onupdate=func.now(),
        default=func.now(),
        server_default=func.now(),
    )


class UpdateCreateDateTimeMixin(CreateDateTimeMixin, UpdateDateTimeMixin): ...
