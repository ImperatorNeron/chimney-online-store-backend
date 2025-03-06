import pytest
from httpx import AsyncClient

from app.schemas.users import (
    LoginUserSchema,
    RegisterUserSchema,
)


@pytest.mark.asyncio(loop_scope="session")
async def test_login(
    async_client: AsyncClient,
    auth_user_payload: RegisterUserSchema,
):
    register_response = await async_client.post(
        url="/api/v1/auth/register",
        json=auth_user_payload.model_dump(mode="json"),
    )

    assert register_response.status_code == 200

    login_credentials = LoginUserSchema(
        username=auth_user_payload.username,
        password=auth_user_payload.password,
    )

    login_response = await async_client.post(
        url="/api/v1/auth/login",
        data=login_credentials.model_dump(mode="json"),
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "refresh_token" in login_response.json()


@pytest.mark.asyncio(loop_scope="session")
async def test_login_with_invalid_credentials(
    async_client: AsyncClient,
    auth_user_payload: RegisterUserSchema,
):
    register_response = await async_client.post(
        url="/api/v1/auth/register",
        json=auth_user_payload.model_dump(mode="json"),
    )

    assert register_response.status_code == 200

    login_credentials = LoginUserSchema(
        username=auth_user_payload.username,
        password="Wrong password",
    )

    login_response = await async_client.post(
        url="/api/v1/auth/login",
        data=login_credentials.model_dump(mode="json"),
    )

    assert login_response.status_code == 401
