from fastapi import FastAPI

import pytest
import pytest_asyncio
from httpx import (
    ASGITransport,
    AsyncClient,
)

from app.db.db import test_database_helper
from app.main import create_app
from app.models.base import BaseModel
from app.utils.unit_of_work import (
    TestUnitOfWork,
    UnitOfWork,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_database_helper.engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield
    async with test_database_helper.engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest.fixture
async def app():
    return create_app()


@pytest.fixture
async def uow():
    async with TestUnitOfWork() as uow:
        yield uow


@pytest.fixture
async def async_client(app: FastAPI):
    app.dependency_overrides[UnitOfWork] = TestUnitOfWork
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
