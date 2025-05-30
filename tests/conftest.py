import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.utils.unit_of_work import TestUnitOfWork, UnitOfWork


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
