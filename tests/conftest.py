from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import ASGITransport, AsyncClient

from app.api.v1.dependencies import get_current_active_auth_superuser, get_current_active_auth_user
from app.main import create_app
from app.schemas.users import ReadUserSchema
from app.utils.unit_of_work import AbstractUnitOfWork, UnitOfWork


@pytest.fixture
async def app():
    application = create_app()
    try:
        FastAPICache.get_prefix()
    except AssertionError:
        FastAPICache.init(InMemoryBackend(), prefix="test-cache")
    return application


@pytest.fixture
def patch_uow(app):
    @asynccontextmanager
    async def _patch(uow_instance):
        async def get_mock_uow():
            yield uow_instance
        app.dependency_overrides[UnitOfWork] = get_mock_uow
        yield
        app.dependency_overrides.pop(UnitOfWork, None)
    return _patch


@pytest.fixture
def patch_superuser(app):
    @asynccontextmanager
    async def _patch():
        async def override_superuser():
            return None

        app.dependency_overrides[get_current_active_auth_superuser] = override_superuser
        yield
        app.dependency_overrides.pop(get_current_active_auth_superuser, None)

    return _patch


@pytest.fixture
def patch_auth_user(app):
    @asynccontextmanager
    async def _patch(user: ReadUserSchema):
        async def override_user():
            return user

        app.dependency_overrides[get_current_active_auth_user] = override_user
        yield
        app.dependency_overrides.pop(get_current_active_auth_user, None)

    return _patch


@pytest.fixture
def mock_uow(mock_repo):
    def _create(repos: dict[str, dict[str, any]]):
        uow = AsyncMock(spec=AbstractUnitOfWork)

        for repo_name, methods in repos.items():
            repo = AsyncMock()
            for method_name, return_value in methods.items():
                setattr(repo, method_name, AsyncMock(return_value=return_value))

            setattr(uow, repo_name, repo)

        uow.__aenter__ = AsyncMock(return_value=uow)
        uow.__aexit__ = AsyncMock(return_value=None)

        uow.commit = AsyncMock()
        uow.rollback = AsyncMock()

        return uow

    return _create


@pytest.fixture
def mock_repo():
    def _create(methods: dict[str, any]):
        repo = AsyncMock()

        for name, value in methods.items():
            method = AsyncMock(return_value=value)
            setattr(repo, name, method)

        return repo

    return _create


@pytest.fixture
async def async_client(app: FastAPI):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
