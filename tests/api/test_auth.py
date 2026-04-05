import pytest
from tests.factories.users import AuthUserPayloadFactory, UserFactory

from app.core.exceptions.common import ItemNotFoundException
from app.services.tokens import JWTTokenService


@pytest.mark.asyncio
async def test_register_success(async_client, mock_uow, patch_uow):
    user_in = AuthUserPayloadFactory.build()
    created_user = UserFactory.build(
        id=1,
        username=user_in.username,
        email=user_in.email,
        phone_number=None,
        first_name=None,
        last_name=None,
        patronymic=None,
        hashed_password=b"hashed-password",
    )
    uow = mock_uow({"users": {"get_or_none": None, "create": created_user}})

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_in.model_dump(),
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["id"] == 1
    assert payload["data"]["username"] == user_in.username
    assert "hashed_password" not in payload["data"]


@pytest.mark.asyncio
async def test_register_conflict_username_exists(async_client, mock_uow, patch_uow):
    user_in = AuthUserPayloadFactory.build(username="taken_user")
    existing_user = UserFactory.build(
        id=2,
        username="taken_user",
        hashed_password=b"hashed-password",
    )
    uow = mock_uow({"users": {"get_or_none": None, "create": None}})

    async def get_or_none_side_effect(**kwargs):
        if kwargs.get("username") == "taken_user":
            return existing_user
        return None

    uow.users.get_or_none.side_effect = get_or_none_side_effect

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_in.model_dump(),
        )

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "username_exists"
    assert payload["errors"][0]["meta"]["username"] == "taken_user"


@pytest.mark.asyncio
async def test_register_conflict_email_exists(async_client, mock_uow, patch_uow):
    user_in = AuthUserPayloadFactory.build(email="taken@example.com")
    existing_user = UserFactory.build(
        id=2,
        username="another_user",
        email="taken@example.com",
        phone_number=None,
        hashed_password=b"hashed-password",
    )
    uow = mock_uow({"users": {"get_or_none": None, "create": None}})

    async def get_or_none_side_effect(**kwargs):
        if kwargs.get("email") == "taken@example.com":
            return existing_user
        return None

    uow.users.get_or_none.side_effect = get_or_none_side_effect

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_in.model_dump(),
        )

    assert response.status_code == 409
    payload = response.json()
    assert payload["data"] is None
    assert payload["errors"][0]["code"] == "email_exists"
    assert payload["errors"][0]["meta"]["email"] == "taken@example.com"


@pytest.mark.asyncio
async def test_register_validation_error_password_mismatch(async_client, mock_uow, patch_uow):
    user_in = AuthUserPayloadFactory.build()
    payload_in = user_in.model_dump()
    payload_in["password"] = "Secret123"
    payload_in["confirm_password"] = "Secret321"
    uow = mock_uow({"users": {"get_or_none": None, "create": None}})

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/register",
            json=payload_in,
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success_sets_refresh_cookie(async_client, mock_uow, patch_uow):
    password = "Secret123"
    user = UserFactory.build(
        id=1,
        username="testuser",
        hashed_password=JWTTokenService.hash_password(password),
    )
    uow = mock_uow({"users": {"get_or_none": user}})

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": password},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "Bearer"
    assert "refresh_token=" in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_login_blocked_user_not_found(async_client, mock_uow, patch_uow):
    uow = mock_uow({"users": {"get_or_none": None}})
    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "missing", "password": "Secret123"},
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["errors"][0]["code"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_login_blocked_invalid_password(async_client, mock_uow, patch_uow):
    user = UserFactory.build(
        id=1,
        username="testuser",
        hashed_password=JWTTokenService.hash_password("CorrectPass123"),
    )
    uow = mock_uow({"users": {"get_or_none": user}})
    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrong"},
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["errors"][0]["code"] == "invalid_credentials"


@pytest.mark.asyncio
async def test_refresh_success_returns_new_access_token(async_client, mock_uow, patch_uow):
    password = "Secret123"
    user = UserFactory.build(
        id=1,
        username="testuser",
        hashed_password=JWTTokenService.hash_password(password),
    )
    uow = mock_uow({"users": {"get_or_none": user, "get": user}})

    async with patch_uow(uow):
        login_response = await async_client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": password},
        )
        assert login_response.status_code == 200

        response = await async_client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_refresh_blocked_without_cookie(async_client, mock_uow, patch_uow):
    uow = mock_uow({"users": {"get": None}})
    async with patch_uow(uow):
        response = await async_client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
    payload = response.json()
    assert payload["errors"][0]["code"] == "invalid_token"


@pytest.mark.asyncio
async def test_refresh_blocked_wrong_token_type(async_client, mock_uow, patch_uow):
    access_token = await JWTTokenService().create_access_token(pk=1, username="testuser")
    uow = mock_uow({"users": {"get": None}})

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": access_token},
        )

    assert response.status_code == 401
    payload = response.json()
    assert payload["errors"][0]["code"] == "invalid_token_type"


@pytest.mark.asyncio
async def test_refresh_blocked_user_not_found(async_client, mock_uow, patch_uow):
    refresh_token = await JWTTokenService().create_refresh_token(pk=1)
    uow = mock_uow({"users": {"get": None}})
    uow.users.get.side_effect = ItemNotFoundException()

    async with patch_uow(uow):
        response = await async_client.post(
            "/api/v1/auth/refresh",
            cookies={"refresh_token": refresh_token},
        )

    assert response.status_code == 404
    payload = response.json()
    assert payload["errors"][0]["code"] == "not_found"


@pytest.mark.asyncio
async def test_logout_deletes_refresh_cookie(async_client):
    response = await async_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert "refresh_token=" in response.headers.get("set-cookie", "")
