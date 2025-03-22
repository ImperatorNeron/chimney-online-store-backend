from abc import ABC, abstractmethod
from typing import Type

from app.db.db import database_helper, test_database_helper
from app.repositories.cart_items import CartItemRepository
from app.repositories.carts import CartRepository
from app.repositories.categories import CategoryRepository
from app.repositories.messages import MessageRepository
from app.repositories.product_images import ProductImageRepository
from app.repositories.products import ProductRepository
from app.repositories.users import UserRepository


class AbstractUnitOfWork(ABC):
    """Abstract base class defining a unit of work pattern for managing
    repositories and database transactions."""

    users: Type[UserRepository]
    messages: Type[MessageRepository]
    categories: Type[CategoryRepository]
    products: Type[ProductRepository]
    products_images: Type[ProductImageRepository]
    cart: Type[CartRepository]
    cart_item: Type[CartItemRepository]

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class BaseUnitOfWork(AbstractUnitOfWork):
    async def __aenter__(self):
        self.session = await self._get_session()
        self.users = UserRepository(session=self.session)
        self.messages = MessageRepository(session=self.session)
        self.categories = CategoryRepository(session=self.session)
        self.products = ProductRepository(session=self.session)
        self.products_images = ProductImageRepository(session=self.session)
        self.cart = CartRepository(session=self.session)
        self.cart_item = CartItemRepository(session=self.session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @abstractmethod
    async def _get_session(self): ...


class UnitOfWork(BaseUnitOfWork):
    """Implementation of the UnitOfWork pattern."""

    async def _get_session(self):
        return database_helper.session_factory()


class TestUnitOfWork(BaseUnitOfWork):
    """Implementation of the UnitOfWork pattern for tests."""

    async def _get_session(self):
        return test_database_helper.session_factory()
