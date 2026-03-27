import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.common import ItemNotFoundException, MultipleResultsFound, RepositoryException
from app.models.base import BaseModel as Model


logger = logging.getLogger(__name__)


class AbstractRepository(ABC):
    """Abstract repository defining modern CRUD operations with ORM models."""

    @abstractmethod
    async def get(
        self,
        options: Optional[list] = None,
        **filters: Any,
    ) -> Model: ...

    @abstractmethod
    async def all(  # noqa
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ) -> list[Model]: ...

    @abstractmethod
    async def create(self, item_in: Model) -> Model: ...

    @abstractmethod
    async def update(self, id: int, item_in: Model) -> Model:  # noqa
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
    async def get_or_none(self, **filters: Any) -> Optional[Model]:
        """Get item or None if not found."""
        ...

    @abstractmethod
    async def bulk_create(self, data_list: list[Model]) -> list[Model]:
        """Create multiple items."""
        ...


class BaseRepository(AbstractRepository):
    model: Model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(self, query: select, filters: dict[str, Any]) -> select:
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

    def _apply_ordering(self, query: select, order_by: list[str]) -> select:
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
        """Загальний метод для отримання однієї моделі з фільтрами."""
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
    ) -> Model:
        return await self._get_model(options=options, **filters)

    async def _all_models(
        self,
        filters: Optional[dict] = None,
        order_by: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        options: Optional[list] = None,
    ) -> list[Model]:
        """Внутрішній метод для отримання списку моделей."""
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
    ) -> list[Model]:
        return await self._all_models(
            filters=filters,
            order_by=order_by,
            limit=limit,
            offset=offset,
            options=options,
        )

    async def create(self, item_in: Model) -> Model:
        try:
            self.session.add(item_in)
            await self.session.flush()
            await self.session.refresh(item_in)
            return item_in
        except Exception as e:
            logger.error("Failed to create item: %s", e, exc_info=True)
            raise RepositoryException()

    async def update(self, id: int, item_in: Model) -> Model:  # noqa
        instance = await self._get_model(id=id)
        try:
            # Копіюємо всі атрибути з item_in, крім id та службових полів SQLAlchemy
            for key, value in item_in.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(instance, key, value)
            await self.session.flush([instance])
            await self.session.refresh(instance)
            return instance
        except Exception as e:
            logger.error("Failed to update item: %s", e, exc_info=True)
            raise RepositoryException()

    async def delete(
        self,
        **filters: Any,
    ) -> None:  # noqa
        instance = await self._get_model(**filters)
        await self.session.delete(instance)

    async def count(self, **filters: Any) -> int:
        query = select(func.count()).select_from(self.model)
        if filters:
            query = self._apply_filters(query, filters)
        return (await self.session.execute(query)).scalar_one()

    async def exists(self, **filters: Any) -> bool:
        query = select(1).select_from(self.model)
        query = self._apply_filters(query, filters)
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar() is not None

    async def get_or_none(self, **filters: Any) -> Optional[Model]:
        query = select(self.model)
        query = self._apply_filters(query, filters)
        result = await self.session.execute(query)
        instance = result.scalars().first()
        return instance if instance else None

    async def bulk_create(self, data_list: list[Model]) -> list[Model]:
        self.session.add_all(data_list)
        await self.session.flush()
        for item in data_list:
            await self.session.refresh(item)
        return data_list
