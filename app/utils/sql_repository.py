from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy import func, insert, Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.base import BaseAppException
from app.core.exceptions.common import ItemNotFoundException, MultipleResultsFound, RepositoryException
from app.models.base import BaseModel as Model


class AbstractRepository(ABC):
    """Abstract repository defining modern CRUD operations."""

    @abstractmethod
    async def get(
        self,
        options: Optional[list] = None,
        **filters: Any,
    ) -> BaseModel: ...

    @abstractmethod
    async def all(  # noqa
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ) -> list[BaseModel]: ...

    @abstractmethod
    async def create(self, item_in: BaseModel) -> BaseModel: ...

    @abstractmethod
    async def update(self, id: int, item_in: BaseModel) -> BaseModel:  # noqa
        """Update existing item."""
        ...

    @abstractmethod
    async def delete(self, id: int) -> None:  # noqa
        """Delete item by ID."""
        ...

    @abstractmethod
    async def exists(self, **filters: Any) -> bool:
        """Check if item exists."""
        ...

    @abstractmethod
    async def count(self, **filters: Any) -> int:
        """Count items matching filters."""
        ...

    @abstractmethod
    async def get_or_none(self, **filters: Any) -> Optional[BaseModel]:
        """Get item or None if not found."""
        ...

    @abstractmethod
    async def bulk_create(self, data_list: list[BaseModel]) -> list[BaseModel]:
        """Create multiple items."""
        ...


class UniqueConstraintViolationError(BaseAppException):
    def __init__(self, fields: list[str], message: str = "Unique constraint violation"):
        self.fields = fields
        self.message = f"{message} on fields: {', '.join(fields)}"
        super().__init__(
            detail=self.message,
            status_code=400,
        )


class RepositoryError(Exception):
    """Base exception for repository errors."""


class BaseRepository:

    model: Model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(self, query: Select, filters: dict[str, Any]) -> Select:
        for field, value in filters.items():
            if "__" in field:
                field_name, operator = field.split("__")
                column = getattr(self.model, field_name)
                if operator == "eq":
                    query = query.where(column == value)
                elif operator == "gt":
                    query = query.where(column > value)
                elif operator == "in":
                    query = query.where(column.in_(value))
            else:
                query = query.where(getattr(self.model, field) == value)
        return query

    def _apply_ordering(self, query: Select, order_by: dict[str]) -> Select:
        for field in order_by:
            direction = "asc"
            if field.startswith("-"):
                direction = "desc"
                field = field[1:]
            column = getattr(self.model, field)
            query = query.order_by(
                column.desc() if direction == "desc" else column.asc(),
            )
        return query

    async def _get_model(
        self,
        options: Optional[list] = None,
        **filters: Any,
    ) -> Model:
        """Загальний метод для отримання моделі з фільтрами."""
        query = select(self.model)

        if options:
            query = query.options(*options)

        if filters:
            query = self._apply_filters(query, filters)

        result = await self.session.execute(query)
        instances = result.scalars().all()

        if len(instances) > 1:
            raise MultipleResultsFound()

        if not instances:
            raise ItemNotFoundException()

        return instances[0]

    async def get(
        self,
        options: Optional[list] = None,
        **filters: Any,
    ) -> BaseModel:
        instance = await self._get_model(options=options, **filters)
        return instance.to_read_model()

    async def _all_models(
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ) -> list[Model]:
        """Внутрішній метод для отримання моделей."""
        query = select(self.model)

        if filters:
            query = self._apply_filters(query, filters)

        if order_by:
            query = self._apply_ordering(query, order_by)

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def all(  # noqa
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ) -> list[BaseModel]:
        models = await self._all_models(
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            options=options,
        )
        return [model.to_read_model() for model in models]

    async def create(self, item_in: BaseModel) -> BaseModel:
        try:
            stmt = (
                insert(self.model).values(**item_in.model_dump()).returning(self.model)
            )
            result = await self.session.execute(stmt)
            instance = result.scalar_one()
            return instance.to_read_model()
        except Exception as e:
            print(e)
            raise RepositoryException()

    async def update(self, id: int, item_in: BaseModel) -> BaseModel:  # noqa
        instance = await self._get_model(id=id)
        try:
            for field, value in item_in.model_dump(exclude_unset=True).items():
                setattr(instance, field, value)
            await self.session.flush([instance])
            await self.session.refresh(instance)
            return instance.to_read_model()
        except Exception:
            raise RepositoryException()

    async def delete(
        self,
        id: int,  # noqa
        **filters: Any,
    ) -> None:  # noqa
        instance = await self._get_model(id=id, **filters)
        await self.session.delete(instance)

    async def exists(self, **filters: Any) -> bool:
        query = select(1).select_from(self.model)
        query = self._apply_filters(query, filters)
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar() is not None

    async def count(self, **filters: Any) -> int:
        query = select(func.count()).select_from(self.model)
        query = self._apply_filters(query, filters)
        result = await self.session.execute(query)
        return result.scalar()

    async def get_or_none(self, **filters: Any) -> Optional[BaseModel]:
        query = select(self.model)
        query = self._apply_filters(query, filters)
        result = await self.session.execute(query)
        instance = result.scalars().first()
        return instance.to_read_model() if instance else None

    async def bulk_create(self, data_list: list[BaseModel]) -> list[BaseModel]:
        instances = [self.model(**data.model_dump()) for data in data_list]
        self.session.add_all(instances)
        await self.session.flush(instances)
        return [instance.to_read_model() for instance in instances]
